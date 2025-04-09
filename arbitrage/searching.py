import requests
import time
from collections import defaultdict


class ExchangePairsFinder:
    """Класс для поиска общих торговых пар на различных биржах"""
    
    # Конфигурация API для каждой биржи (без изменений)
    EXCHANGES_CONFIG = {
        'Binance': {
            'base_url': 'https://api.binance.com',
            'symbols_endpoint': '/api/v3/exchangeInfo',
            'price_endpoint': '/api/v3/ticker/price',
            'parser': lambda data: float(data['price']),
            'symbol_normalizer': lambda s: s.replace('USDT', '').upper()
        },
        'Bybit': {
            'base_url': 'https://api.bybit.com',
            'symbols_endpoint': '/v5/market/instruments-info',
            'price_endpoint': '/v5/market/tickers',
            'parser': lambda data: float(data['result']['list'][0]['lastPrice']),
            'extra_params': {'category': 'spot'},
            'symbol_normalizer': lambda s: s.replace('USDT', '').upper()
        },
        'Kraken': {
            'base_url': 'https://api.kraken.com',
            'symbols_endpoint': '/0/public/AssetPairs',
            'price_endpoint': '/0/public/Ticker',
            'parser': lambda data: float(list(data['result'].values())[0]['c'][0]),
            'symbol_normalizer': lambda s: s.replace('USD', '').upper(),
            'symbol_filter': lambda s: 'usd' in s.lower() and not s.lower().endswith('a.usd')
        },
        'OKX': {
            'base_url': 'https://www.okx.com',
            'symbols_endpoint': '/api/v5/public/instruments',
            'price_endpoint': '/api/v5/market/ticker',
            'parser': lambda data: float(data['data'][0]['last']),
            'extra_params': {'instType': 'SPOT'},
            'symbol_normalizer': lambda s: s.replace('-USDT', '').upper()
        },
        'Huobi': {
            'base_url': 'https://api.huobi.pro',
            'symbols_endpoint': '/v1/common/symbols',
            'price_endpoint': '/market/detail/merged',
            'parser': lambda data: float(data['tick']['close']),
            'symbol_normalizer': lambda s: s.replace('usdt', '').upper()
        },
        'Gate.io': {
            'base_url': 'https://api.gateio.ws',
            'symbols_endpoint': '/api/v4/spot/currency_pairs',
            'price_endpoint': '/api/v4/spot/tickers',
            'parser': lambda data: float(data[0]['last']),
            'symbol_normalizer': lambda s: s.replace('_USDT', '').upper()
        }
    }

    @staticmethod
    def normalize_symbol(exchange, symbol):
        """Нормализует символ для сравнения между биржами"""
        normalizer = ExchangePairsFinder.EXCHANGES_CONFIG[exchange].get('symbol_normalizer', lambda s: s)
        return normalizer(symbol)

    def get_all_usdt_pairs(self):
        """Получаем все USDT-пары, доступные на всех биржах"""
        exchange_symbols = {}
        normalized_pairs = defaultdict(set)
        
        for exchange, config in ExchangePairsFinder.EXCHANGES_CONFIG.items():
            try:
                url = config['base_url'] + config['symbols_endpoint']
                params = config.get('extra_params', {})
                
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                if exchange == 'Binance':
                    symbols = [s['symbol'] for s in data['symbols'] 
                            if s['symbol'].endswith('USDT') and s['status'] == 'TRADING']
                elif exchange == 'Bybit':
                    symbols = [s['symbol'] for s in data['result']['list'] 
                            if s['symbol'].endswith('USDT') and s['status'] == 'Trading']
                elif exchange == 'Kraken':
                    symbols = [p for p in data['result'] 
                            if config.get('symbol_filter', lambda _: True)(p) and 
                            'usd' in data['result'][p]['wsname'].lower()]
                elif exchange == 'OKX':
                    symbols = [s['instId'] for s in data['data'] 
                            if s['instId'].endswith('-USDT') and s['state'] == 'live']
                elif exchange == 'Huobi':
                    symbols = [s['symbol'] for s in data['data'] 
                            if s['symbol'].lower().endswith('usdt') and s['state'] == 'online']
                elif exchange == 'Gate.io':
                    symbols = [s['id'] for s in data 
                            if s['id'].endswith('_USDT') and s['trade_status'] == 'tradable']
                
                exchange_symbols[exchange] = symbols
                #print(f"{exchange}: получено {len(symbols)} торговых пар")
                
                # Нормализуем и добавляем символы
                for symbol in symbols:
                    normalized = self.normalize_symbol(exchange, symbol)
                    normalized_pairs[normalized].add((exchange, symbol))
                
            except Exception as e:
                print(f"Ошибка получения пар с {exchange}: {str(e)[:200]}")
                exchange_symbols[exchange] = []
        
        # Находим пары, доступные на всех биржах (минимум на 3 биржах для примера)
        common_pairs = []
        for norm_symbol, exchanges in normalized_pairs.items():
            if len(exchanges) >= 3:  # Можно изменить на 6 для всех бирж
                common_pairs.append({
                    'normalized': norm_symbol,
                    'pairs': dict(exchanges)
                })
        
        #print(f"\nНайдено {len(common_pairs)} общих торговых пар (минимум на 3 биржах):")
        for pair in common_pairs[:1000]:  # Показываем первые 10 для примера
            #print(pair['normalized'])
        
            return common_pairs


# Для использования в другом модуле:
# from exchange_pairs_finder import ExchangePairsFinder
# finder = ExchangePairsFinder()
# common_pairs = finder.get_all_usdt_pairs()

if __name__ == "__main__":
    finder = ExchangePairsFinder()
    common_pairs = finder.get_all_usdt_pairs()