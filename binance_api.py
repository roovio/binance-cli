import hashlib
import hmac
import random
import time
from urllib.parse import urlencode, urljoin

import requests

BINANCE_API_ENDPOINTS = [
    "https://api.binance.com",
    "https://api1.binance.com",
    "https://api2.binance.com",
    "https://api3.binance.com"
]


def get_api_endpoint():
    return random.choice(BINANCE_API_ENDPOINTS)


class BinanceQueryError(Exception):
    def __init__(self, status_code: int = 0, data: str = ""):
        self.status_code = status_code
        if data:
            self.code = data['code']
            self.msg = data['msg']
        else:
            self.code = None
            self.msg = None
        message = f"{status_code} [{self.code}] {self.msg}"

        super().__init__(message)


class Binance:
    def __init__(self, api_key: str, secret: str) -> None:
        self.api_key = str(api_key)
        self.secret = str(secret)

    def _api_query_public(self, command: str, data: dict = {}) -> dict:
        url = urljoin(get_api_endpoint(), command)
        resp = requests.get(url, params=data)
        return resp.json()

    def _api_query_private(self, operation: callable, command: str, data: dict = {}) -> dict:
        url = urljoin(get_api_endpoint(), command)

        headers = {'X-MBX-APIKEY': self.api_key}

        data['timestamp'] = int(time.time() * 1000)
        data['recvWindow'] = 5000
        query_string = urlencode(data)
        signature = hmac.new(self.secret.encode('utf-8'), query_string.encode('utf-8'),
                                     hashlib.sha256).hexdigest()
        #print(f"signature={signature}")
        data['signature'] = signature

        resp = operation(url, headers=headers, params=data)

        if resp.status_code != 200:
            raise BinanceQueryError(status_code=resp.status_code, data=resp.json())

        return resp.json()

    # def createBuyOrder(self, symbol: str, price: int, quantity: float, timeInForce: str):
    #     passed_price_filter, price = binance_filters.get_price_filter(symbol, self.exchange_info, price)
    #     if not passed_price_filter:
    #         raise BinanceFilterError(symbol, price, "Price")

    #     passed_quantity_filter, quantity = binance_filters.get_quantity_filter(symbol, self.exchange_info, quantity)
    #     if not passed_quantity_filter:
    #         raise BinanceFilterError(symbol, quantity, "Quantity")

    #     params = {
    #         'symbol': symbol,
    #         'side': 'BUY',
    #         'type': 'LIMIT',
    #         'timeInForce': timeInForce,
    #         'quantity': quantity,
    #         'price': price
    #     }

    #     order = self._api_query_private(requests.post, '/api/v3/order', params)

    # def createBuyMarketOrder(self, symbol: str, quantity: float):
    #     passed_quantity_filter, quantity = binance_filters.get_quantity_filter(symbol, self.exchange_info, quantity)
    #     if not passed_quantity_filter:
    #         raise BinanceFilterError(symbol, quantity, "Quantity")

    #     params = {'symbol': symbol, 'side': 'BUY', 'type': 'MARKET', 'quantity': quantity}

    #     order = self._api_query_private(requests.post, '/api/v3/order', params)

    # def createSellOrder(self, symbol: str, price: int, quantity: float, timeInForce: str):
    #     passed_price_filter, price = binance_filters.get_price_filter(symbol, self.exchange_info, price)
    #     if not passed_price_filter:
    #         raise BinanceFilterError(symbol, price, "Price")

    #     passed_quantity_filter, quantity = binance_filters.get_quantity_filter(symbol, self.exchange_info, quantity)
    #     if not passed_quantity_filter:
    #         raise BinanceFilterError(symbol, quantity, "Quantity")

    #     params = {
    #         'symbol': symbol,
    #         'side': 'SELL',
    #         'type': 'LIMIT',
    #         'timeInForce': timeInForce,
    #         'quantity': quantity,
    #         'price': price
    #     }

    #     order = self._api_query_private(requests.post, '/api/v3/order', params)

    # def createSellMarketOrder(self, symbol: str, quantity: float):
    #     passed_quantity_filter, quantity = binance_filters.get_quantity_filter(symbol, self.exchange_info, quantity)
    #     if not passed_quantity_filter:
    #         raise BinanceFilterError(symbol, quantity, "Quantity")

    #     params = {'symbol': symbol, 'side': 'SELL', 'type': 'MARKET', 'quantity': quantity}

    #     order = self._api_query_private(requests.post, '/api/v3/order', params)


    def symbolPriceTicker(self, symbol: str) -> dict:
        return self._api_query_public("/api/v3/ticker/price", {"symbol": symbol})

    #type: "SPOT", "MARGIN", "FUTURES"
    def dailyAccountSnapshot(self, account_type: str) -> dict:
        return self._api_query_private(requests.get, "/sapi/v1/accountSnapshot", {"type": account_type})

    def allCoinsInformation(self) -> dict:
        return self._api_query_private(requests.get, "/sapi/v1/capital/config/getall")

    def accountInformation(self) -> dict:
        return self._api_query_private(requests.get, "/api/v3/account")
    
    def currentOpenOrders(self, symbol: str = None) -> dict:
        params = dict()
        if symbol:
            params['symbol'] = symbol
        return self._api_query_private(requests.get, "api/v3/openOrders", params)

    def cancelOrder(self, symbol: str, orderId: int) -> dict:
        params = {'symbol': symbol, 'orderId': orderId}
        return self._api_query_private(requests.delete, '/api/v3/order', params)

    def cancelAllOpenOrders(self, symbol: str) -> dict:
        params = {'symbol': symbol}
        return self._api_query_private(requests.delete, '/api/v3/openOrders', params)
