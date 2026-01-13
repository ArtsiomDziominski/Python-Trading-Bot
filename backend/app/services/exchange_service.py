import ccxt
from typing import Dict, Any
from app.models.bot import Exchange

class ExchangeService:
    def __init__(self):
        self.exchanges = {}

    def get_exchange(self, exchange_name: Exchange, api_key: str, api_secret: str) -> ccxt.Exchange:
        exchange_id = exchange_name.value
        if exchange_id not in self.exchanges:
            exchange_class = getattr(ccxt, exchange_id)
            self.exchanges[exchange_id] = exchange_class({
                'apiKey': api_key,
                'secret': api_secret,
                'enableRateLimit': True,
            })
        return self.exchanges[exchange_id]

    def create_order(
        self,
        exchange_name: Exchange,
        api_key: str,
        api_secret: str,
        symbol: str,
        side: str,
        type: str,
        amount: float,
        price: float = None
    ) -> Dict[str, Any]:
        exchange = self.get_exchange(exchange_name, api_key, api_secret)
        params = {}
        if type == 'limit' and price:
            params['price'] = price
        
        order = exchange.create_order(symbol, type, side, amount, price, params)
        return order

    def get_order_status(
        self,
        exchange_name: Exchange,
        api_key: str,
        api_secret: str,
        order_id: str,
        symbol: str
    ) -> Dict[str, Any]:
        exchange = self.get_exchange(exchange_name, api_key, api_secret)
        order = exchange.fetch_order(order_id, symbol)
        return order
