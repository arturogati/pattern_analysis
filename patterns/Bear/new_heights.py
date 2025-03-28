import requests
import pandas as pd
import parsing
class NewHeights:
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

    def get_historical_candles(self, symbol, interval="60", limit=10):
        """
        Получает исторические данные о свечах с Bybit.
        
        :param symbol: Торговая пара (например, "BTCUSDT").
        :param interval: Интервал свечи (в минутах). По умолчанию "60" (часовая свеча).
        :param limit: Количество свечей. По умолчанию 10.
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
        - Первая свеча красная и меньше второй
        - Вторая свеча красная и меньше третьей
        - Третья свеча красная и больше четвертой
        - Четвертая свеча зеленая и больше пятой
        - Пятая свеча красная и имеет тень сверху
        - Шестая свеча зеленая
        - Седьмая свеча красная
        - Восьмая свеча зеленая
        - Девятая свеча зеленая
        - Десятая свеча зеленая
        
        :param df: DataFrame с историческими данными о свечах.
        :return: True, если условие соблюдается, иначе False.
        """
        if len(df) < 10:
            return False
            
        # Проверяем первую свечу (красная и меньше второй)
        first_red = df.iloc[0]["close"] < df.iloc[0]["open"]
        first_less_than_second = df.iloc[0]["close"] < df.iloc[1]["close"]
        
        # Проверяем вторую свечу (красная и меньше третьей)
        second_red = df.iloc[1]["close"] < df.iloc[1]["open"]
        second_less_than_third = df.iloc[1]["close"] < df.iloc[2]["close"]
        
        # Проверяем третью свечу (красная и больше четвертой)
        third_red = df.iloc[2]["close"] < df.iloc[2]["open"]
        third_greater_than_fourth = df.iloc[2]["close"] > df.iloc[3]["close"]
        
        # Проверяем четвертую свечу (зеленая и больше пятой)
        fourth_green = df.iloc[3]["close"] > df.iloc[3]["open"]
        fourth_greater_than_fifth = df.iloc[3]["close"] > df.iloc[4]["close"]
        
        # Проверяем пятую свечу (красная и имеет тень сверху)
        fifth_red = df.iloc[4]["close"] < df.iloc[4]["open"]
        fifth_has_upper_shadow = df.iloc[4]["high"] > max(df.iloc[4]["open"], df.iloc[4]["close"])
        
        # Проверяем шестую свечу (зеленая)
        sixth_green = df.iloc[5]["close"] > df.iloc[5]["open"]
        
        # Проверяем седьмую свечу (красная)
        seventh_red = df.iloc[6]["close"] < df.iloc[6]["open"]
        
        # Проверяем восьмую свечу (зеленая)
        eighth_green = df.iloc[7]["close"] > df.iloc[7]["open"]
        
        # Проверяем девятую свечу (зеленая)
        ninth_green = df.iloc[8]["close"] > df.iloc[8]["open"]
        
        # Проверяем десятую свечу (зеленая)
        tenth_green = df.iloc[9]["close"] > df.iloc[9]["open"]
        
        return (
            first_red and first_less_than_second and
            second_red and second_less_than_third and
            third_red and third_greater_than_fourth and
            fourth_green and fourth_greater_than_fifth and
            fifth_red and fifth_has_upper_shadow and
            sixth_green and
            seventh_red and
            eighth_green and
            ninth_green and
            tenth_green
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
                # Получаем последние 10 свечей
                df = self.get_historical_candles(symbol, interval="60", limit=10)
                
                if self.check_condition(df):
                    parsing.parser.check_teck(symbols=symbol)
                    if parsing.parser.check_teck(symbols=symbol) == 1:
                        print(f"\nУсловие соблюдается для {symbol}")
            
            except Exception as e:
                print(f"Ошибка при обработке {symbol}: {e}")
                continue

# Пример использования
if __name__ == "__main__":
    # Создаем объект класса CandleScanner
    scanner = NewHeights()
    
    # Запускаем сканирование всех активов
    scanner.scan_all_symbols()