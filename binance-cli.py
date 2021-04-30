import sys
import json
import time
import fileinput
import pandas
from pandas import DataFrame


from binance_api import Binance
import config

PROMPT="> "

D = "D"
I = "I"
W = "W"
E = "E"
def msg(t, *args):
    print(f"{t}:", *args)

def pretty_json(s):
    print(json.dumps(s, indent=4, sort_keys=True))


api = Binance(config.api_key, config.secret)

LOW_BALANCE_THRESHOLD = 0.01



def cmd_ping():
    t = time.time()
    api.ping()
    print(f"{(time.time()-t)*1000:.2f}ms")

def cmd_account():
    response = api.dailyAccountSnapshot("SPOT")
    pretty_json(response)

def cmd_market_price(symbol: str):
    response = api.symbolPriceTicker(symbol)
    print(float(response['price']))

def cmd_equiv_diff(price_a: float, price_b: float, amount: float):
    equiv = (price_a - price_b) * amount
    print(f"{equiv:8.8f}")

def cmd_status_list_equity():
    print("Equity")
    print("------")
    response = api.allCoinsInformation()
    df = DataFrame.from_dict(response)
    df = df.filter(items=["coin", "name", "free", "locked"])#, "storage", "trading"])
    df['free'] = pandas.to_numeric(df['free'])
    df['locked'] = pandas.to_numeric(df['locked'])
    df = df.loc[lambda df:  (df['free'] > LOW_BALANCE_THRESHOLD) | (df['locked'] > LOW_BALANCE_THRESHOLD), :]
    
    prices_df = DataFrame.from_dict(api.allSymbolsPriceTicker()).set_index(keys='symbol')
    prices_df['price'] = pandas.to_numeric(prices_df['price'])

    prices_usd=[]
    for idx, data in df.iterrows():
        coin = data['coin']
        price_usd = 0
        if coin != "USDT":
            if coin + "USDT" in prices_df.index:
                price_usd = prices_df.at[coin + "USDT", 'price']
            elif coin + "BTC" in prices_df.index and "BTCUSDT" in prices_df.index:
                price_usd = prices_df.at[coin + "BTC", 'price'] * prices_df.at["BTCUSDT", 'price']
            elif coin + "ETH" in prices_df.index and "ETHUSDT" in prices_df.index:
                price_usd = prices_df.at[coin + "ETH", 'price'] * prices_df.at["ETHUSDT", 'price']
            else:
                price_usd = 0
        else:
            price_usd = 1
        prices_usd.append(price_usd)
    df['rate $'] = prices_usd
    df['equiv $'] = (df['free'] + df['locked']) * df['rate $']

    print(df.to_string(index=False))

 
def cmd_status_list_open_orders():
    print("Open Orders")
    print("-----------")

    response = api.currentOpenOrders()
    df = DataFrame.from_dict(response)
    df['time'] = pandas.to_datetime(df['time'], unit="ms")
    df['price'] = pandas.to_numeric(df['price'])
    df['stopPrice'] = pandas.to_numeric(df['stopPrice'])
    df['executedQty'] = pandas.to_numeric(df['executedQty'])
    df['origQty'] = pandas.to_numeric(df['origQty'])
    df['origQuoteOrderQty'] = pandas.to_numeric(df['origQuoteOrderQty'])
    df['cummulativeQuoteQty'] = pandas.to_numeric(df['cummulativeQuoteQty'])
    df['total'] = df['price'] * df['origQty']
    #df['stopPrice'] = df['stopPrice'].transform(lambda s: s if s > 0.00000001 else '-')   #note: breaks decimal point alignment because column type is no longer numeric
    df = df.sort_values(by="time", ascending=False)
    df = df.filter(items=[ "orderId", "time", "symbol", "type", "side", "price", "origQty", "executedQty", "total", "stopPrice", "status" ])
    print(df.to_string(index=False))


def cmd_status():
    cmd_status_list_equity()
    print("")
    cmd_status_list_open_orders()
    

def cmd_order_history(symbol: str):
    print("Order History")
    print("-------------")

    response = api.allOrders(symbol)
    df = DataFrame.from_dict(response)
    df = df.loc[df['status'] == "FILLED", :]
    df['time'] = pandas.to_datetime(df['time'], unit="ms")
    df['price'] = pandas.to_numeric(df['price'])
    df['executedQty'] = pandas.to_numeric(df['executedQty'])
    df['origQty'] = pandas.to_numeric(df['origQty'])
    df['origQuoteOrderQty'] = pandas.to_numeric(df['origQuoteOrderQty'])
    df['cummulativeQuoteQty'] = pandas.to_numeric(df['cummulativeQuoteQty'])
    df['average'] = df['cummulativeQuoteQty'] / df['executedQty']
    #df['price'] = df['price'].transform(lambda s: s if s > 0.00000001 else 'Market')  #note: breaks decimal point alignment because column type is no longer numeric
    df = df.sort_values(by="time", ascending=False)
    df = df.filter(items=[ "orderId", "time", "symbol", "type", "side", "average", "price", "executedQty", "origQty", "origQuoteOrderQty", "cummulativeQuoteQty"])
    print(df.to_string(index=False))


def parse_qty(symbol: str, amount_str: str):
    convert = False
    if amount_str == "$":
        amount = float(amount_str[1:])
        amount_tokens = amount / api.symbolPriceTicker(symbol)
        msg(I, f"converted ${amount} to {amount_tokens} {symbol} tokens using market price ticker")
        return amount_tokens
    else:
        amount_tokens = float(amount_str)
        return amount_tokens


def cmd_order_buy_market(symbol: str, qty: float) -> dict:
    return api.createMarketOrder(symbol, "BUY", qty)

def cmd_order_buy_limit(symbol: str, limit_str: str, qty: float) -> dict:
    [ot,price] = limit_str.split("=")
    limit_price = float(price)
    return api.createLimitOrder(symbol, "BUY", qty, limit_price)

def cmd_order_buy(tokens: list[str]):
    symbol = tokens[0]
    qty = parse_qty(symbol, tokens[2])
    order_type_str = tokens[1]
    r = {}
    if order_type_str == "market":
        r = cmd_order_buy_market(symbol, qty)
    elif "limit" in order_type_str:
        r = cmd_order_buy_limit(symbol, order_type_str, qty)
    else:
        msg(E, "invalid order type", order_type_str)
        return
    print(f"{r['status']} order {r['orderId']}")


def cmd_order_sell_market(symbol: str, qty: float):
    return api.createMarketOrder(symbol, "SELL", qty)

def cmd_order_sell_limit(symbol: str, limit_str: str, qty: float):
    [ot,price] = limit_str.split("=")
    limit_price = float(price)
    return api.createLimitOrder(symbol, "SELL", qty, limit_price)

def cmd_order_sell(tokens: list[str]):
    symbol = tokens[0]
    qty = parse_qty(symbol, tokens[2])
    order_type_str = tokens[1]
    r = {}
    if order_type_str == "market":
        r = cmd_order_sell_market(symbol, qty)
    elif "limit" in order_type_str:
        r = cmd_order_sell_limit(symbol, order_type_str, qty)
    else:
        msg(E, "invalid order type", order_type_str)
        return
    print(f"{r['status']} order {r['orderId']}")


def cmd_order_cancel_id(symbol: str, order_id: int):
    msg(I, f"canceling order {order_id} on {symbol}")
    response = api.cancelOrder(symbol, order_id)
    print(response['status'])


def cmd_order_cancel_all_symbol(symbol: str):
    msg(I, f"canceling all orders on {symbol}!")
    response = api.cancelAllOpenOrders(symbol)
    for order_status in response:
        print(f"order {order_status['orderId']} -> {order_status['status']}")


def cmd_order_cancel_all():
    #msg(I, "canceling EVERY order!")
    msg(E, "not implemented")


def execute_command(tokens: list[str]):
    if len(tokens) >= 1:
        cmd = tokens[0]
        if cmd == "ping":
            cmd_ping()
        elif cmd == "price":
            cmd_market_price(tokens[1])
        elif cmd == "equivdiff":
            cmd_equiv_diff(float(tokens[1]), float(tokens[2]), float(tokens[3]))
        elif cmd == "status":
            cmd_status()
        elif cmd == "oh":
            cmd_order_history(tokens[1])
        elif cmd == "buy":
            cmd_order_buy(tokens[1:])
        elif cmd == "sell":
            cmd_order_sell(tokens[1:])
        elif cmd == "cancel":
            try:
                symbol  = tokens[1]
                if symbol == "ALL":
                    cmd_order_cancel_all()
                else:
                    order_id = tokens[2]
                    if order_id == "ALL":
                        cmd_order_cancel_all_symbol(symbol)
                    else:
                        cmd_order_cancel_id(symbol, int(order_id))
            except Exception as e:
                msg(E, f"{e}")
        else:
            msg(E, f"unknown command: {cmd}")


def next_command(stdin):
    print("\n" + PROMPT, end="")
    sys.stdout.flush()
    line = stdin.readline().rstrip()
    tokens = line.split()
    execute_command(tokens)


def run_command_loop():
    stdin = fileinput.input()
    while True:
        #try:
        next_command(stdin)
        #except Exception as e:
        #    msg(E, f"{e}")


def run_oneshot(tokens: list[str]):
    execute_command(tokens)


if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[1] == "--":
        run_oneshot(sys.argv[2:])
    else:
        print("Binance CLI started")
        run_command_loop()
