import requests
import pandas as pd
import numpy as np

class EnhancedBullishWindowScanner:
    def __init__(self):
        """
        Инициализация класса EnhancedBullishWindowScanner.
        """
        self.base_url = "https://api.bybit.com/v5/market"

    def get_all_symbols(self):
        """
        Получает список всех торговых пар (активов) на Bybit.
        """
        url = f"{self.base_url}/instruments-info"
        params = {"category": "linear"}
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            raise Exception(f"Ошибка запроса: {response.status_code}, {response.text}")
        
        data = response.json()
        if data["retCode"] != 0:
            raise Exception(f"Ошибка API: {data['retMsg']}")
        
        return [item["symbol"] for item in data["result"]["list"] if item["symbol"].endswith("USDT")]

    def get_historical_candles(self, symbol, interval="60", limit=7):
        """
        Получает исторические данные о свечах с Bybit.
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
        
        # Преобразование данных
        numeric_cols = ["open", "high", "low", "close", "volume", "turnover"]
        df[numeric_cols] = df[numeric_cols].astype(float)
        df["timestamp"] = pd.to_datetime(df["timestamp"].astype(int), unit="ms")
        
        # Добавляем расчет скользящих средних для объема
        df['volume_ma'] = df['volume'].rolling(window=5).mean()
        
        return df

    def check_bullish_window_enhanced(self, df):
        """
        Улучшенная проверка паттерна Bullish Window с анализом 7 свечей:
        1. Подтверждение нисходящего тренда (минимум 4 из 6 предыдущих свечей красные)
        2. Стандартные условия Bullish Window для последних двух свечей
        3. Подтверждение объема (объем на паттерне выше среднего)
        4. Проверка на сопротивление (цена не должна встречать сильное сопротивление)
        """
        if len(df) < 7:
            return False

        # 1. Проверка нисходящего тренда
        prev_candles = df.iloc[:5]  # Свечи до паттерна
        red_count = sum(prev_candles["close"] < prev_candles["open"])
        if red_count < 4:
            return False

        # 2. Анализ последних двух свечей (потенциальный Bullish Window)
        first_candle = df.iloc[5]  # Первая свеча паттерна
        second_candle = df.iloc[6]  # Вторая свеча паттерна
        
        # Основные условия Bullish Window
        first_red = first_candle["close"] < first_candle["open"]
        second_green = second_candle["close"] > second_candle["open"]
        open_below_close = second_candle["open"] < first_candle["close"]
        close_above_open = second_candle["close"] > first_candle["open"]
        has_gap = second_candle["low"] > first_candle["high"]
        
        if not (first_red and second_green and open_below_close and close_above_open and has_gap):
            return False

        # 3. Проверка объема
        volume_ok = second_candle["volume"] > df['volume_ma'].iloc[6]
        
        # 4. Проверка на сопротивление (цена не должна быть ниже важного уровня)
        resistance_check = second_candle["close"] > df['high'].iloc[:5].mean()
        
        return volume_ok and resistance_check

    def scan_all_symbols(self):
        """
        Сканирует все активы с расширенными условиями.
        """
        symbols = self.get_all_symbols()
        print(f"Сканирование {len(symbols)} активов на паттерн Bullish Window")
        
        results = []
        for symbol in symbols:
            try:
                df = self.get_historical_candles(symbol, interval="60", limit=7)
                if self.check_bullish_window_enhanced(df):
                    # Добавляем дополнительную аналитику
                    trend_strength = self.calculate_trend_strength(df)
                    volume_ratio = df["volume"].iloc[6] / df['volume_ma'].iloc[6]
                    results.append({
                        "symbol": symbol,
                        "trend_strength": trend_strength,
                        "volume_ratio": volume_ratio,
                        "gap_size": (df.iloc[6]["low"] - df.iloc[5]["high"]) / df.iloc[5]["high"] * 100
                    })
                    print(f"Найден паттерн для {symbol} | Сила тренда: {trend_strength:.2f} | Объем: x{volume_ratio:.1f}")
            
            except Exception as e:
                print(f"Ошибка при обработке {symbol}: {str(e)[:50]}...")
                continue

        if results:
            print("\nНайденные паттерны Bullish window:")
            results_df = pd.DataFrame(results).sort_values("volume_ratio", ascending=False)
            a=(results_df.to_string(index=False))
            #a=results[0]['symbol']
            return a
        else:
            print("\nПаттерн bullish window не обнаружен ни на одном активе.")

    def calculate_trend_strength(self, df):
        """
        Рассчитывает силу нисходящего тренда (0-1).
        """
        red_candles = df["close"].iloc[:5] < df["open"].iloc[:5]
        price_decline = (df["close"].iloc[0] - df["close"].iloc[4]) / df["close"].iloc[0]
        return (sum(red_candles)/5 + price_decline) / 2

    def run(self):
        self.scan_all_symbols()

if __name__ == "__main__":
    scanner = EnhancedBullishWindowScanner()
    scanner.run()