import requests
import time
from collections import defaultdict
from searching import ExchangePairsFinder

class ExchangePairsSaver:
    def get_all_usdt_pairs(self):
        # Здесь должен быть реальный код получения пар с бирж
        # Временная заглушка с примером пар
        finder = ExchangePairsFinder()
        pairs_data = finder.get_all_usdt_pairs()
        raw_pairs = []
        for pair in pairs_data:
            a=f"{pair['normalized']}:"
            raw_pairs.append(a)# Пример сырых данных с биржи
        
        #print(raw_pairs)
        #time.sleep(100)
        processed_pairs = []
        for pair in raw_pairs:
            # Удаляем слэш и преобразуем к единому формату
            #normalized = pair.replace('/', '').upper()
            pair = pair+'USDT'
            processed_pairs.append(pair.replace(':', ''))
            print
        return processed_pairs
        
def get_exchanges_config(pair):
    """Генерируем конфиг бирж для конкретной пары"""
    return {
        'Binance': {
            'symbol': pair,
            'url': 'https://api.binance.com/api/v3/ticker/price',
            'parser': lambda data: float(data['price']),
            'params': {'symbol': pair}
        },
        'Bybit': {
            'symbol': pair,
            'url': 'https://api.bybit.com/v5/market/tickers',
            'parser': lambda data: float(data['result']['list'][0]['lastPrice']),
            'params': {'category': 'spot', 'symbol': pair}
        },
        'Kraken': {
            'symbol': pair.replace('USDT', 'USD'),
            'url': 'https://api.kraken.com/0/public/Ticker',
            'parser': lambda data: float(data['result'][list(data['result'].keys())[0]]['c'][0]),
            'params': {'pair': pair.replace('USDT', 'USD')}
        },
        'OKX': {
            'symbol': pair.replace('USDT', '-USDT'),
            'url': 'https://www.okx.com/api/v5/market/ticker',
            'parser': lambda data: float(data['data'][0]['last']),
            'params': {'instId': pair.replace('USDT', '-USDT')}
        },
        'Huobi': {
            'symbol': pair.lower(),
            'url': 'https://api.huobi.pro/market/detail/merged',
            'parser': lambda data: float(data['tick']['close']),
            'params': {'symbol': pair.lower()}
        },
        'Gate.io': {
            'symbol': pair.replace('USDT', '_USDT'),
            'url': 'https://api.gateio.ws/api/v4/spot/tickers',
            'parser': lambda data: float(data[0]['last']),
            'params': {'currency_pair': pair.replace('USDT', '_USDT')}
        }
    }

def fetch_price(exchange_name, config):
    """Получаем текущую цену с указанной биржи"""
    try:
        response = requests.get(
            config['url'],
            params=config['params'],
            timeout=5
        )
        response.raise_for_status()

        if exchange_name == 'Bybit':
            if not response.json().get('result'):
                print(f"Bybit API: No data for {config['symbol']}")
                return None

        return config['parser'](response.json())

    except requests.exceptions.RequestException as e:
        print(f"Network error ({exchange_name}): {str(e)[:100]}")
    except (ValueError, KeyError, IndexError) as e:
        print(f"Parsing error ({exchange_name}): {str(e)[:100]}")
    return None

def get_top_spreads(prices):
    """Вычисляем все возможные спреды между биржами"""
    valid_prices = {k: v for k, v in prices.items() if v is not None}
    spreads = []
    
    for buy_ex, buy_price in valid_prices.items():
        for sell_ex, sell_price in valid_prices.items():
            if buy_ex == sell_ex:
                continue
                
            spread = sell_price - buy_price
            spread_pct = (spread / buy_price) * 100
            
            spreads.append({
                'buy_ex': buy_ex,
                'sell_ex': sell_ex,
                'buy_price': buy_price,
                'sell_price': sell_price,
                'spread': spread,
                'spread_pct': spread_pct
            })
    
    return sorted(spreads, key=lambda x: abs(x['spread_pct']), reverse=True)[:3]

def main():
    finder = ExchangePairsSaver()
    
    #while True:
    pairs_data = finder.get_all_usdt_pairs()
    
    for pair in pairs_data:
        normalized_pair = pair
        #print(f"\n[ {time.strftime('%H:%M:%S')} ] Analyzing pair: {normalized_pair}")
        
        EXCHANGES = get_exchanges_config(normalized_pair)
        prices = {}
        
        for name, config in EXCHANGES.items():
            prices[name] = fetch_price(name, config)
            if prices[name]:
                pass
                #print(f"{prices[name]:.4f}")
            else:
                print(f"{name}: Failed to fetch price")
        
        top_spreads = get_top_spreads(prices)
        
        if top_spreads:
            print(f"\n🔍 Top 3 Arbitrage Opportunities: {pair}")
            for i, arb in enumerate(top_spreads, 1):
                print(f"{i}. Buy on {arb['buy_ex']:8} ({arb['buy_price']:8.4f}) "
                        f"| Sell on {arb['sell_ex']:8} ({arb['sell_price']:8.4f}) "
                        f"| Spread: ${arb['spread']:.4f} ({arb['spread_pct']:.2f}%)")
        else:
            print("No valid data to calculate spreads.")
        
        time.sleep(1)  # Пауза между парами
    
    print("\n🔁 Restarting scan cycle...")
        #time.sleep(5)  # Пауза между полными циклами сканирования

if __name__ == "__main__":
    main()