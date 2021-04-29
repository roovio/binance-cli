# binance-cli

`binance-cli` is a tool that implements shall-like interface to Binance trading account. 

## Usage

Interactive mode:

```
   python binance-cli.py 
```

One-shot mode:

```
   python binance-cli.py -- <COMMAND> [ARGs]
```

## Commands

### status

Display spot account equity and pending orders

```
status
```

### oh (Order History)

Display spot account order history for specified symbol

```
oh <SYMBOL>
```

### buy

Place a buy order

```
buy <SYMBOL> <ORDER_TYPE>[=PRICE1[,PRICE2,PRICE3]] <TOKENS|CURRENCY>
```

| Argument        | Description |
| --------------- | ----------- |
| `SYMBOL`        | the trading pair, example: BTCUSDT
| `ORDER_TYPE`    | any of the following: `market`, `limit`, `stop`, `oco`
| `PRICEn`        | see below
| `TOKENS`        | number of tokens to buy. Example: if SYMBOL=BTCUSDT and TOKENS=1 this means buy 1 BTC
| `$CURRENCY`     | currency to spend (calculate tokens automatically). Must be prefixed by "$". <br> Example: if `SYMBOL`=`BTCUSDT` and `CURRENCY`=1000 this means spend 1000 USDT to buy BTC at specified price |

Each `ORDER_TYPE` requires specific amount of PRICE tokens:

| `ORDER_TYPE` | `PRICE` tokens to specify |
| -------------|---------------------------|
| `market`     | -
| `limit`      | `PRICE1` is limit price
| `stop`       | `PRICE1` is stop price,  `PRICE2` is stop limit price
| `oco`        | `PRICE1` is limit price, `PRICE2` is stop price, `PRICE3` is stop limit price

### sell

Place a sell order. For arguments, see 'buy' command

```
sell <SYMBOL> <ORDER_TYPE>[=PRICE1[,PRICE2,PRICE3]] <TOKENS>
```

### cancel

Cancels one or more orders

```
cancel <SYMBOL|'ALL'> [ID|'ALL']
```

| Argument        | Description |
| --------------- | ----------- |
| `SYMBOL`        | symbol to cancel orders for. Can be "ALL" so that orders for all symbols are canceled.
| `ID`            | order ID to cancel.  IDs are listed by the `status` command. Can be "ALL" to cancel all orders for symbol
