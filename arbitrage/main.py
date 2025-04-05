import requests
import time
from collections import defaultdict

def get_kraken_price(symbol='XBTUSD'):
    url = 'https://api.kraken.com/0/public/Ticker'
    params = {'pair': symbol}
    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        if 'result' in data:
            return float(data['result'][symbol]['c'][0])
        print(f"Kraken API Error: {data.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"Error fetching Kraken price: {str(e)[:100]}")
    return None

def get_bybit_price(symbol='BTCUSDT'):
    url = 'https://api.bybit.com/v2/public/tickers'
    params = {'symbol': symbol}
    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        if data['ret_code'] == 0 and data['result']:
            return float(data['result'][0]['last_price'])
        print(f"Bybit API Error: {data.get('ret_msg', 'Unknown error')}")
    except Exception as e:
        print(f"Error fetching Bybit price: {str(e)[:100]}")
    return None

def get_okx_price(symbol='BTC-USDT'):
    url = 'https://www.okx.com/api/v5/market/ticker'
    params = {'instId': symbol}
    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        if data['code'] == '0' and data['data']:
            return float(data['data'][0]['last'])
        print(f"OKX API Error: {data.get('msg', 'Unknown error')}")
    except Exception as e:
        print(f"Error fetching OKX price: {str(e)[:100]}")
    return None

def get_binance_price(symbol='BTCUSDT'):
    url = 'https://api.binance.com/api/v3/ticker/price'
    params = {'symbol': symbol}
    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        return float(data['price'])
    except Exception as e:
        print(f"Error fetching Binance price: {str(e)[:100]}")
    return None

def get_huobi_price(symbol='btcusdt'):
    url = 'https://api.huobi.pro/market/detail/merged'
    params = {'symbol': symbol}
    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        if 'tick' in data:
            return float(data['tick']['close'])
        print(f"Huobi API Error: {data.get('err-msg', 'Unknown error')}")
    except Exception as e:
        print(f"Error fetching Huobi price: {str(e)[:100]}")
    return None

def get_gateio_price(symbol='BTC_USDT'):
    url = 'https://api.gateio.ws/api/v4/spot/tickers'
    params = {'currency_pair': symbol}
    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        if data and isinstance(data, list):
            return float(data[0]['last'])
        print("Gate.io API Error: Empty response")
    except Exception as e:
        print(f"Error fetching Gate.io price: {str(e)[:100]}")
    return None

def get_coinex_price(symbol='BTCUSDT'):
    url = 'https://api.coinex.com/v1/market/ticker'
    params = {'market': symbol}
    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        if data and 'data' in data:
            return float(data['data']['ticker']['last'])
        print(f"CoinEx API Error: {data.get('message', 'Unknown error')}")
    except Exception as e:
        print(f"Error fetching CoinEx price: {str(e)[:100]}")
    return None

def get_cryptocom_price(symbol='BTC_USDT'):
    url = 'https://api.crypto.com/v2/public/get-ticker'
    params = {'instrument_name': symbol}
    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        if data['code'] == 0 and data['result']:
            return float(data['result']['data'][0]['a'])
        print(f"Crypto.com API Error: {data.get('message', 'Unknown error')}")
    except Exception as e:
        print(f"Error fetching Crypto.com price: {str(e)[:100]}")
    return None

def get_bingx_price(symbol='BTC-USDT'):
    url = 'https://api.bingx.com/api/v3/ticker/price'
    params = {'symbol': symbol}
    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        if 'price' in data:
            return float(data['price'])
        print(f"BingX API Error: {data.get('msg', 'Unknown error')}")
    except Exception as e:
        print(f"Error fetching BingX price: {str(e)[:100]}")
    return None

def get_bitget_price(symbol='BTCUSDT'):
    url = 'https://api.bitget.com/api/spot/v1/market/ticker'
    params = {'symbol': symbol}
    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        if data and 'data' in data:
            return float(data['data']['close'])
        print(f"Bitget API Error: {data.get('msg', 'Unknown error')}")
    except Exception as e:
        print(f"Error fetching Bitget price: {str(e)[:100]}")
    return None

def compare_prices():
    exchanges = {
        'Kraken': ('XBTUSD', get_kraken_price),
        'Bybit': ('BTCUSDT', get_bybit_price),
        'OKX': ('BTC-USDT', get_okx_price),
        'Binance': ('BTCUSDT', get_binance_price),
        'Huobi': ('btcusdt', get_huobi_price),
        'Gate.io': ('BTC_USDT', get_gateio_price),
        'CoinEx': ('BTCUSDT', get_coinex_price),
        'Crypto.com': ('BTC_USDT', get_cryptocom_price),
        'BingX': ('BTC-USDT', get_bingx_price),
        'Bitget': ('BTCUSDT', get_bitget_price)
    }
    
    while True:
        prices = defaultdict(lambda: None)
        start_time = time.time()
        
        print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Fetching prices from {len(exchanges)} exchanges...")
        
        # Получаем цены
        for name, (symbol, func) in exchanges.items():
            prices[name] = func(symbol)
        
        # Фильтруем только валидные цены
        valid_prices = {k: v for k, v in prices.items() if v is not None}
        
        if len(valid_prices) >= 2:
            max_price = max(valid_prices.values())
            min_price = min(valid_prices.values())
            price_diff = max_price - min_price
            avg_price = sum(valid_prices.values()) / len(valid_prices)
            price_diff_percent = (price_diff / avg_price) * 100
            
            print("\nCurrent BTC Prices:")
            for exchange, price in sorted(valid_prices.items(), key=lambda x: x[1], reverse=True):
                print(f"{exchange:>12}: ${price:>12,.2f} {'↑' if price == max_price else '↓' if price == min_price else ''}")
            
            print(f"\nArbitrage Opportunity: ${price_diff:,.4f} ({price_diff_percent:.4f}%)")
            print(f"Best Buy:  {min(valid_prices.items(), key=lambda x: x[1])[0]} at ${min_price:,.2f}")
            print(f"Best Sell: {max(valid_prices.items(), key=lambda x: x[1])[0]} at ${max_price:,.2f}")
            
            # Дополнительная статистика
            spread = {k: ((v - min_price)/min_price*100) for k, v in valid_prices.items()}
            print("\nPrice Spreads from Lowest:")
            for exchange, spread_pct in sorted(spread.items(), key=lambda x: x[1], reverse=True):
                print(f"{exchange:>12}: {spread_pct:.4f}%")
        else:
            print("Error: Not enough valid prices to compare (need at least 2 exchanges)")
        
        elapsed = time.time() - start_time
        sleep_time = max(0, 5 - elapsed)  # 5 секунд между запросами
        time.sleep(sleep_time)

if __name__ == "__main__":
    compare_prices()