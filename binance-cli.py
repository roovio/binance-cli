import sys
import json
import fileinput
from enum import Enum, auto



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


class OrderType(Enum):
    MARKET = auto()
    LIMIT = auto()
    STOP = auto()
    OCO = auto()

class OrderArgs():
    def __init__(self, tokens: list[str]):
        self.limit_price=None
        self.stop_price=None
        self.stop_limit_price=None
        try:
            self.ticker = tokens[0]

            if tokens[1] == "market":
                self.type = OrderType.MARKET
            else:
                [ot,prices] = tokens[1].split("=")
                if ot == "limit":
                    self.type = OrderType.LIMIT
                    self.limit_price = float(prices)
                elif ot == "stop":
                    price_list = prices.split(",")
                    self.type = OrderType.STOP
                    self.stop_price = float(price_list[0])
                    self.stop_limit_price = float(price_list[1])
                elif ot == "oco":
                    price_list = prices.split(",")
                    self.type = OrderType.OCO
                    self.limit_price = float(price_list[0])
                    self.stop_price = float(price_list[1])
                    self.stop_limit_price = float(price_list[2])
                else:
                    raise SyntaxError("invalid order type")

            if tokens[2][0] == "$":
                self.position_size = float(tokens[2][1:])
                self.position_size_in_tokens = False
            else:
                self.position_size = float(tokens[2])
                self.position_size_in_tokens = True

        except:
            raise SyntaxError()

    def __str__(self):
        s = f"{self.ticker} {self.type}"
        if self.limit_price:
            s +=f" limit={self.limit_price}"
        if self.stop_price:
            s +=f" stop={self.stop_price}"
        if self.stop_limit_price:
            s +=f" stop_limit={self.stop_limit_price}"
        if self.position_size_in_tokens:
            s += f" position={self.position_size}"
        else:
            s += f" position=$ {self.position_size}"
        return s

def cmd_account():
    response = api.dailyAccountSnapshot("SPOT")
    pretty_json(response)

def cmd_market_price(symbol: str):
    response = api.symbolPriceTicker(symbol)
    print(response['price'])


def cmd_status_list_equity():
    print("Equity:")
    response = api.allCoinsInformation()
    for item in filter(lambda x: float(x['free']) != 0, response):
        print(f"{item['coin']} {item['name']} {float(item['free'])}")

def cmd_status_list_equity1():
    print("Equity:")
    response = api.accountInformation()
    for item in response['balances']:
        print(f"{item['asset']}  {float(item['free'])}")

def cmd_status_list_open_orders():
    print("Open orders:")
    response = api.currentOpenOrders()

    print("symbol order_id type price stop_price qty status")

    for item in response:
        symbol = item['symbol']
        order_id=  int(item['orderId'])
        price = float(item['price'])
        qty = float(item['executedQty'])
        status = item['status']
        otype = item['type']
        stop = float(item['stopPrice'])

        print(f"{symbol} {order_id} {otype} {price} {stop} {qty} {status}")

def cmd_status():
    #msg(I, "cmd status")
    cmd_status_list_equity()
    #cmd_status_list_equity1()
    cmd_status_list_open_orders()

def cmd_order_buy(order: OrderArgs):
    msg(I, f"cmd order buy : {order}")

def cmd_order_sell(order: OrderArgs):
    msg(I, f"cmd order sell : {order}")

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
        if cmd == "account":
            cmd_account()
        elif cmd == "price":
            cmd_market_price(tokens[1])
        elif cmd == "status":
            cmd_status()
        elif cmd == "buy":
            try:
                cmd_order_buy(OrderArgs(tokens[1:]))
            except SyntaxError as e:
                msg(E, "failed to parse order arguments")
        elif cmd == "sell":
            try:
                cmd_order_sell(OrderArgs(tokens[1:]))
            except SyntaxError as e:
                msg(E, "failed to parse order arguments")
            pass
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
