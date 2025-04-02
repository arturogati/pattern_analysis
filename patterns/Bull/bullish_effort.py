import requests
import pandas as pd
class BullishEffort:
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

    def get_historical_candles(self, symbol, interval="60", limit=9):
        """
        Получает исторические данные о свечах с Bybit.
        
        :param symbol: Торговая пара (например, "BTCUSDT").
        :param interval: Интервал свечи (в минутах). По умолчанию "60" (часовая свеча).
        :param limit: Количество свечей. По умолчанию 9.
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
        - Первая свеча зеленая и самая высокая
        - Вторая свеча зеленая и больше третьей
        - Третья свеча красная
        - Четвертая свеча красная и имеет тень снизу
        - Пятая свеча зеленая и больше шестой
        - Шестая свеча красная
        - Седьмая свеча зеленая и меньше восьмой
        - Восьмая свеча красная и меньше девятой
        - Девятая свеча красная
        
        :param df: DataFrame с историческими данными о свечах.
        :return: True, если условие соблюдается, иначе False.
        """
        if len(df) < 9:
            return False
            
        # Проверяем первую свечу (зеленая и самая высокая)
        first_green = df.iloc[0]["close"] > df.iloc[0]["open"]
        first_highest = df.iloc[0]["high"] == df["high"].max()
        
        # Проверяем вторую свечу (зеленая и больше третьей)
        second_green = df.iloc[1]["close"] > df.iloc[1]["open"]
        second_greater_than_third = df.iloc[1]["close"] > df.iloc[2]["close"]
        
        # Проверяем третью свечу (красная)
        third_red = df.iloc[2]["close"] < df.iloc[2]["open"]
        
        # Проверяем четвертую свечу (красная и имеет тень снизу)
        fourth_red = df.iloc[3]["close"] < df.iloc[3]["open"]
        fourth_has_lower_shadow = df.iloc[3]["low"] < min(df.iloc[3]["open"], df.iloc[3]["close"])
        
        # Проверяем пятую свечу (зеленая и больше шестой)
        fifth_green = df.iloc[4]["close"] > df.iloc[4]["open"]
        fifth_greater_than_sixth = df.iloc[4]["close"] > df.iloc[5]["close"]
        
        # Проверяем шестую свечу (красная)
        sixth_red = df.iloc[5]["close"] < df.iloc[5]["open"]
        
        # Проверяем седьмую свечу (зеленая и меньше восьмой)
        seventh_green = df.iloc[6]["close"] > df.iloc[6]["open"]
        seventh_less_than_eighth = df.iloc[6]["close"] < df.iloc[7]["close"]
        
        # Проверяем восьмую свечу (красная и меньше девятой)
        eighth_red = df.iloc[7]["close"] < df.iloc[7]["open"]
        eighth_less_than_ninth = df.iloc[7]["close"] < df.iloc[8]["close"]
        
        # Проверяем девятую свечу (красная)
        ninth_red = df.iloc[8]["close"] < df.iloc[8]["open"]
        
        return (
            first_green and first_highest and
            second_green and second_greater_than_third and
            third_red and
            fourth_red and fourth_has_lower_shadow and
            fifth_green and fifth_greater_than_sixth and
            sixth_red and
            seventh_green and seventh_less_than_eighth and
            eighth_red and eighth_less_than_ninth and
            ninth_red
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
                # Получаем последние 9 свечей
                df = self.get_historical_candles(symbol, interval="60", limit=9)
                
                # Проверяем условие
                if self.check_condition(df):
                    print(f"\nУсловие соблюдается для {symbol}")
            
            except Exception as e:
                print(f"Ошибка при обработке {symbol}: {e}")
                continue

# Пример использования
if __name__ == "__main__":
    # Создаем объект класса CandleScanner
    scanner = BullishEffort()
    
    # Запускаем сканирование всех активов
    scanner.scan_all_symbols()