import requests
import pandas as pd

class HammerPattern:
    def __init__(self):
        """
        Инициализация класса CandleScanner.
        """
        self.base_url = "https://api.bybit.com/v5/market"

    def get_all_symbols(self):
        """
        Получает список всех торговых пар (активов) на Bybit.
        
        :return: Список торговых пар.
        """
        url = f"{self.base_url}/instruments-info"
        params = {
            "category": "linear"  # Линейные фьючерсы (USDT-пары)
        }
        response = requests.get(url, params=params)
        if response.status_code != 200:
            raise Exception(f"Ошибка запроса: {response.status_code}, {response.text}")
        
        data = response.json()
        if data["retCode"] != 0:
            raise Exception(f"Ошибка API: {data['retMsg']}")
        
        # Извлекаем список символов и фильтруем только USDT-пары
        symbols = [item["symbol"] for item in data["result"]["list"] if item["symbol"].endswith("USDT")]
        return symbols

    def get_historical_candles(self, symbol, interval="60", limit=6):
        """
        Получает исторические данные о свечах с Bybit.
        
        :param symbol: Торговая пара (например, "BTCUSDT").
        :param interval: Интервал свечи (в минутах). По умолчанию "60" (часовая свеча).
        :param limit: Количество свечей. По умолчанию 6.
        :return: DataFrame с данными о свечах.
        """
        url = f"{self.base_url}/kline"
        params = {
            "category": "linear",
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }
        response = requests.get(url, params=params)
        if response.status_code != 200:
            raise Exception(f"Ошибка запроса: {response.status_code}, {response.text}")
        
        data = response.json()
        if data["retCode"] != 0:
            raise Exception(f"Ошибка API: {data['retMsg']}")
        
        candles = data["result"]["list"]
        df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "volume", "turnover"])
        
        # Преобразуем данные в числовой формат
        df[["open", "high", "low", "close", "volume", "turnover"]] = df[["open", "high", "low", "close", "volume", "turnover"]].astype(float)
        
        # Преобразуем timestamp в читаемый формат даты
        df["timestamp"] = pd.to_datetime(df["timestamp"].astype(int), unit="ms")
        
        return df

    def check_condition(self, df):
        """
        Проверяет, соблюдается ли условие:
        - Первые 3 свечи красные.
        - Последние 3 свечи зелёные.
        
        :param df: DataFrame с историческими данными о свечах.
        :return: True, если условие соблюдается, иначе False.
        """
       # Проверяем первые 3 свечи (красные)
        first_three_green = all(df.iloc[i]["close"] > df.iloc[i]["open"] for i in range(3))
            
        # Проверяем последние 3 свечи (красные)
        last_three_red = all(df.iloc[i]["close"] < df.iloc[i]["open"] for i in range(3, 6))
        
        return first_three_green and last_three_red

    def scan_all_symbols(self):
        """
        Сканирует все активы на Bybit и выводит название пары, если соблюдается условие.
        """
        # Получаем список всех торговых пар
        symbols = self.get_all_symbols()
        print(f"Найдено {len(symbols)} активов для сканирования.")
        
        # Перебираем все активы
        for symbol in symbols:
            try:
                # Получаем последние 6 свечей
                df = self.get_historical_candles(symbol, interval="60", limit=6)
                
                # Проверяем условие
                if self.check_condition(df):
                    print(f"\nУсловие соблюдается для {symbol}")
            
            except Exception as e:
                print(f"Ошибка при обработке {symbol}: {e}")
                continue

# Пример использования
if __name__ == "__main__":
    # Создаем объект класса CandleScanner
    scanner = HammerPattern()
    
    # Запускаем сканирование всех активов
    scanner.scan_all_symbols()