import requests


import requests

def get_all_spot_symbols():
    """
    Получает список всех спотовых торговых пар на Bybit.
    
    Returns:
        list: Список всех спотовых торговых пар (например, ['BTCUSDT', 'ETHUSDT', ...])
    
    Raises:
        Exception: При ошибке запроса или обработки данных
    """
    base_url = "https://api.bybit.com/v5/market"
    url = f"{base_url}/instruments-info"
    params = {"category": "spot"}
    
    try:
        # Выполняем запрос с таймаутом
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # Проверяем HTTP ошибки
        
        data = response.json()
        
        # Проверяем код ответа API
        if data.get("retCode") != 0:
            error_msg = data.get("retMsg", "Unknown error")
            raise Exception(f"API error: {error_msg}")
        
        # Извлекаем все символы
        return [item["symbol"] for item in data["result"]["list"]]
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Request failed: {str(e)}")
    except (KeyError, ValueError) as e:
        raise Exception(f"Data processing error: {str(e)}")

# Пример использования
try:
    spot_symbols = get_all_spot_symbols()
    print(f"Found {len(spot_symbols)} spot trading pairs")
    print("Sample symbols:", spot_symbols[:10])  # Показываем первые 10 символов
except Exception as e:
    print(f"Error: {str(e)}")


def get_symbol_price(symbol):
    url = "https://api.bybit.com/v5/market/tickers"
    params = {
        "category": "spot",  # или "spot", "inverse" в зависимости от рынка
        "symbol": symbol,
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Проверка на ошибки HTTP (404, 500 и т.д.)
        data = response.json()
        
        # Проверяем структуру ответа Bybit v5
        if data.get("retCode") == 0 and data.get("result"):
            ticker = data["result"]["list"][0]  # Берём первый тикер из списка
            return float(ticker["lastPrice"])
        
        print(f"Ошибка для {symbol}: {data.get('retMsg', 'Некорректный формат ответа')}")
        return None
    
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса для {symbol}: {e}")
        return None
    except (KeyError, IndexError, ValueError) as e:
        print(f"Ошибка парсинга данных для {symbol}: {e}")
        return None

# Пример запроса цен
symbols = get_all_spot_symbols()

for symbol in symbols:
    price = get_symbol_price(symbol)
    if price is not None:
        print(f"{symbol}: {price}")