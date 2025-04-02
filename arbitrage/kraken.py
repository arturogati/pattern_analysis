import requests
from time import sleep

def get_all_spot_symbols_kraken():
    """
    Получает все спотовые торговые пары с биржи Kraken
    Returns:
        list: Список всех пар в формате ['XBTUSDT', 'ETHUSDT', ...]
    """
    url = "https://api.kraken.com/0/public/AssetPairs"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("error"):
            raise Exception(f"API error: {data['error']}")
            
        # Фильтруем только спотовые пары (не фьючерсы)
        return [
            pair 
            for pair in data["result"] 
            if not data["result"][pair].get("wsname", "").endswith("PERP")
        ]
        
    except Exception as e:
        print(f"Error getting symbols: {str(e)}")
        return []

def get_asset_name(full_symbol):
    """Извлекает название актива из полного символа Kraken"""
    # Удаляем 'X' для BTC (XBT -> BTC) и 'Z' для других валют
    clean_symbol = full_symbol.replace('XBT', 'BTC').replace('X', '').replace('Z', '')
    # Берем первую часть до цифр или конца строки
    asset = ''.join([c for c in clean_symbol if not c.isdigit()])
    return asset.split('USD')[0] if 'USD' in asset else asset

def get_symbol_price_kraken(symbol):
    """
    Получает текущую цену для указанной пары
    Args:
        symbol (str): Торговая пара Kraken (например 'XBTUSDT')
    Returns:
        float: Последняя цена или None при ошибке
    """
    url = "https://api.kraken.com/0/public/Ticker"
    params = {"pair": symbol}
    
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if data.get("error"):
            print(f"Error for {symbol}: {data['error']}")
            return None
            
        if not data.get("result"):
            print(f"No data available for {symbol}")
            return None
            
        # Получаем первый ключ в result (иногда отличается от запрошенного символа)
        result_key = next(iter(data["result"]))
        return float(data["result"][result_key]["c"][0])  # Последняя цена закрытия
        
    except Exception as e:
        print(f"Request error for {symbol}: {str(e)}")
        return None

def main():
    # Получаем все спотовые пары
    print("Getting list of all spot trading pairs from Kraken...")
    symbols = get_all_spot_symbols_kraken()
    
    if not symbols:
        print("Failed to get symbols list")
        return
        
    print(f"Total pairs: {len(symbols)}")
    
    # Собираем уникальные активы
    unique_assets = {}
    for symbol in symbols:
        asset_name = get_asset_name(symbol)
        if asset_name not in unique_assets:
            unique_assets[asset_name] = symbol
    
    print("Unique assets:", list(unique_assets.keys())[:10])
    
    # Получаем цены для уникальных активов
    print("\nGetting current prices for unique assets...")
    successful = 0
    
    for i, (asset_name, symbol) in enumerate(unique_assets.items()):
        price = get_symbol_price_kraken(symbol)
        if price is not None:
            print(f"{i+1}. {asset_name}: {price}")
            successful += 1
        sleep(0.3)  # Kraken имеет более строгие лимиты
    
    print(f"\nSuccessfully retrieved prices for {successful} out of {len(unique_assets)} unique assets")

if __name__ == "__main__":
    main()