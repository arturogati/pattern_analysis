import requests
import pandas as pd


class FallingStar:
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
        - Первая свеча красная и меньше второй.
        - Вторая свеча красная и меньше третьей.
        - Третья свеча зелёная и имеет тень сверху.
        - Четвёртая свеча зелёная и больше пятой.
        - Пятая свеча зелёная и больше шестой.
        - Шестая свеча зелёная.
        
        :param df: DataFrame с историческими данными о свечах.
        :return: True, если условие соблюдается, иначе False.
        """
        # Проверяем первую свечу (красная и меньше второй)
        first_red = df.iloc[0]["close"] < df.iloc[0]["open"]
        first_less_than_second = df.iloc[0]["close"] < df.iloc[1]["close"]
        
        # Проверяем вторую свечу (красная и меньше третьей)
        second_red = df.iloc[1]["close"] < df.iloc[1]["open"]
        second_less_than_third = df.iloc[1]["close"] < df.iloc[2]["close"]
        
        # Проверяем третью свечу (зелёная и имеет тень сверху)
        third_green = df.iloc[2]["close"] > df.iloc[2]["open"]
        third_has_upper_shadow = df.iloc[2]["high"] > df.iloc[2]["close"]
        
        # Проверяем четвёртую свечу (зелёная и больше пятой)
        fourth_green = df.iloc[3]["close"] > df.iloc[3]["open"]
        fourth_greater_than_fifth = df.iloc[3]["close"] > df.iloc[4]["close"]
        
        # Проверяем пятую свечу (зелёная и больше шестой)
        fifth_green = df.iloc[4]["close"] > df.iloc[4]["open"]
        fifth_greater_than_sixth = df.iloc[4]["close"] > df.iloc[5]["close"]
        
        # Проверяем шестую свечу (зелёная)
        sixth_green = df.iloc[5]["close"] > df.iloc[5]["open"]
        
        return (
            first_red and first_less_than_second and
            second_red and second_less_than_third and
            third_green and third_has_upper_shadow and
            fourth_green and fourth_greater_than_fifth and
            fifth_green and fifth_greater_than_sixth and
            sixth_green
        )

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
                
                if self.check_condition(df):
                    print(f"\nУсловие соблюдается для {symbol}")
                    
            except Exception as e:
                continue

# Пример использования
if __name__ == "__main__":
    # Создаем объект класса CandleScanner
    scanner = FallingStar()
    
    # Запускаем сканирование всех активов
    scanner.scan_all_symbols()