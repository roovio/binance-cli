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

    def ping(self) -> dict:
        return self._api_query_public("/api/v3/ping")

    def allSymbolsPriceTicker(self) -> dict:
        return self._api_query_public("/api/v3/ticker/price")

    def symbolPriceTicker(self, symbol: str) -> dict:
        return self._api_query_public("/api/v3/ticker/price", {"symbol": symbol})

    #type: "SPOT", "MARGIN", "FUTURES"
    def dailyAccountSnapshot(self, account_type: str) -> dict:
        return self._api_query_private(requests.get, "/sapi/v1/accountSnapshot", {"type": account_type})

    def allCoinsInformation(self) -> dict:
        return self._api_query_private(requests.get, "/sapi/v1/capital/config/getall")

    def accountInformation(self) -> dict:
        return self._api_query_private(requests.get, "/api/v3/account")
    
    def allOrders(self, symbol: str) -> dict:
        return self._api_query_private(requests.get, "api/v3/allOrders", { 'symbol': symbol})

    def currentOpenOrders(self, symbol: str = None) -> dict:
        params = dict()
        if symbol:
            params['symbol'] = symbol
        return self._api_query_private(requests.get, "api/v3/openOrders", params)

    def createMarketOrder(self, symbol: str, side: str, quantity: float) -> dict:
        params = {
            'symbol': symbol,
            'side': side,
            'type': 'MARKET',
            'quantity': quantity
        }
        #print("market order", params)
        return self._api_query_private(requests.post, "/api/v3/order", params)

    def createLimitOrder(self, symbol: str, side: str, quantity: float, price: float) -> dict:
        params = {
            'symbol': symbol,
            'side': side,
            'type': 'LIMIT',
            'timeInForce': 'GTC',
            'quantity': quantity,
            'price': f"{price:8.8f}" # if price is too small default conversion will format float using
                                     # scientific notation which exchange API does not understand
        }
        #print("limit order", params)
        return self._api_query_private(requests.post, "/api/v3/order", params)

    def cancelOrder(self, symbol: str, orderId: int) -> dict:
        params = {'symbol': symbol, 'orderId': orderId}
        return self._api_query_private(requests.delete, '/api/v3/order', params)

    def cancelAllOpenOrders(self, symbol: str) -> dict:
        params = {'symbol': symbol}
        return self._api_query_private(requests.delete, '/api/v3/openOrders', params)
