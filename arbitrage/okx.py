import requests
from time import sleep

def get_all_spot_symbols_okx():
    """
    Получает все активные спотовые торговые пары с биржи OKX
    Returns:
        list: Список всех активных пар в формате ['BTC-USDT', 'ETH-USDT', ...]
    """
    url = "https://www.okx.com/api/v5/public/instruments"
    params = {"instType": "SPOT"}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("code") != "0":
            raise Exception(f"API error: {data.get('msg', 'Unknown error')}")
            
        # Фильтруем только активные пары (state == "live")
        return [
            item["instId"] 
            for item in data["data"] 
            if item.get("state") == "live"
        ]
        
    except Exception as e:
        print(f"Error getting symbols: {str(e)}")
        return []

def get_asset_name(full_symbol):
    """Извлекает название актива из полного символа (например, BTC из BTC-USDT)"""
    return full_symbol.split('-')[0]

def get_symbol_price_okx(symbol):
    """
    Получает текущую цену для указанной пары
    Args:
        symbol (str): Торговая пара в формате OKX (например 'BTC-USDT')
    Returns:
        float: Последняя цена или None при ошибке
    """
    url = "https://www.okx.com/api/v5/market/ticker"
    params = {"instId": symbol}
    
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if data.get("code") != "0":
            print(f"Error for {symbol}: {data.get('msg', 'No data')}")
            return None
            
        if not data.get("data"):
            print(f"No data available for {symbol}")
            return None
            
        return float(data["data"][0]["last"])
        
    except Exception as e:
        print(f"Request error for {symbol}: {str(e)}")
        return None

def main():
    # Получаем все активные спотовые пары
    print("Getting list of all active spot trading pairs from OKX...")
    symbols = get_all_spot_symbols_okx()
    
    if not symbols:
        print("Failed to get symbols list")
        return
        
    print(f"Total active pairs: {len(symbols)}")
    print("Sample pairs:", [get_asset_name(s) for s in symbols[:10]])
    
    # Получаем цены для всех пар (первые 20 для примера)
    print("\nGetting current prices...")
    successful = 0
    
    for i, symbol in enumerate(symbols[:20]):
        price = get_symbol_price_okx(symbol)
        if price is not None:
            asset_name = get_asset_name(symbol)  # Извлекаем только название актива
            print(f"{i+1}. {asset_name}: {price}")
            successful += 1
        sleep(0.2)  # Задержка для соблюдения лимитов API
    
    print(f"\nSuccessfully retrieved prices for {successful} out of {min(20, len(symbols))} assets")

if __name__ == "__main__":
    main()