# binance-cli

`binance-cli` is a tool that implements shall-like interface to Binance trading account. 

## Usage

Interactive mode:

```
   ./binance-cli
```

One-shot mode:

```
   ./binance-cli -- <COMMAND> [ARGs]
```

## Commands

### equity

Display spot account equity

```
equity
```

### oo (Open Orders)

Display spot account open orders

```
oo
```

### status

A combination of `equity` and `oo` commands as a single command. Display spot account equity and open orders.

```
status
```

### oh (Order History)

Display spot account order history for specified symbol

```
oh <SYMBOL>
```

### equiv_order

Calculate equivalent cummulative order since timestamp till now

```
equiv_order <SYMBOL> <TIMESTAMP>
```

Example:

```
$ ./binance-cli -- equiv_order CDTETH "2021-04-29 10:32:26"

Equivalent cummulative signed order since 2021-04-29 10:32:26+03:00

          time side  executedQty  cummulativeQuoteQty
05-02 22:05:46  BUY      20000.0           0.29640000
05-02 08:24:27  BUY      10000.0           0.15112524
05-01 23:39:49  BUY      10000.0           0.15532485
05-01 04:45:07  BUY      20000.0           0.33000000
05-01 00:36:24 SELL      20000.0           0.33760000
04-30 13:44:04 SELL      20000.0           0.32400000
04-30 13:38:13  BUY      20000.0           0.30880000
04-30 11:24:20  BUY      20000.0           0.32940000
04-29 22:13:55 SELL      53594.0           0.79426308
04-29 20:49:09 SELL       6406.0           0.09576970
04-29 20:14:00  BUY      30000.0           0.44820000
04-29 20:11:45  BUY      30000.0           0.44807564
04-29 19:47:15 SELL      21140.0           0.31710000
04-29 19:37:19 SELL       1462.0           0.02194462
04-29 17:18:04  BUY      20000.0           0.29880000
04-29 10:32:26  BUY       2602.0           0.03988866
equiv quote qty: 0.91533699
equiv tokens qty: 60000.00000000
equiv price: 0.00001526
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
| `CURRENCY$`     | currency to spend (calculate tokens automatically). Must be suffixed by '$'. <br> Example: if `SYMBOL`=`BTCUSDT` and `CURRENCY`= 1000 this means spend 1000 USDT to buy BTC at specified price |

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
sell <SYMBOL> <ORDER_TYPE>[=PRICE1[,PRICE2,PRICE3]] [TOKENS]
```

   Unlike in `buy` command `TOKENS` parameter can be omitted when selling. 
   In such case the algorithm finds the matching coin and it's equity and attempts to sell all holdings for the coin.

### cancel

Cancels one or more orders

```
cancel <ID|SYMBOL|'ALL'>
```

| Argument        | Description |
| --------------- | ----------- |
| `ID`            | Cancel order by ID.  IDs are listed by the `oo` or `status`command. No need to specify the symbol -- determined automatically.
| `SYMBOL`        | Cancel all existing orders for specified symbol
| `ALL`           | Cancel all existing orders in the account
