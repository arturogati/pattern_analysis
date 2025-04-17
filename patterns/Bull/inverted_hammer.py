import requests
import pandas as pd
import numpy as np

class EnhancedInvertedHammerScanner:
    def __init__(self):
        """
        Инициализация класса EnhancedInvertedHammerScanner.
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

    def get_historical_candles(self, symbol, interval="60", limit=6):
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
        
        return df

    def check_inverted_hammer(self, df):
        """
        Улучшенная проверка паттерна Inverted Hammer с анализом 6 свечей:
        1. Подтверждение нисходящего тренда (минимум 3 из 5 предыдущих свечей красные)
        2. Стандартные условия Inverted Hammer для последней свечи
        3. Подтверждение объема (объем последней свечи выше среднего)
        """
        if len(df) < 6:
            return False

        # 1. Проверка нисходящего тренда (минимум 3 из 5 предыдущих свечей красные)
        prev_candles = df.iloc[:5]
        red_count = sum(prev_candles["close"] < prev_candles["open"])
        if red_count < 3:
            return False

        # 2. Анализ последней свечи (потенциальный Inverted Hammer)
        last_candle = df.iloc[5]
        body_size = abs(last_candle["close"] - last_candle["open"])
        upper_shadow = last_candle["high"] - max(last_candle["open"], last_candle["close"])
        lower_shadow = min(last_candle["open"], last_candle["close"]) - last_candle["low"]
        
        # Основные условия Inverted Hammer
        is_small_body = body_size <= upper_shadow / 2
        has_small_lower_shadow = lower_shadow <= body_size / 2
        has_long_upper_shadow = upper_shadow >= 2 * body_size
        
        # 3. Проверка объема (объем последней свечи выше среднего)
        avg_volume = df["volume"].iloc[:5].mean()
        volume_ok = last_candle["volume"] > avg_volume

        return is_small_body and has_small_lower_shadow and has_long_upper_shadow and volume_ok

    def scan_all_symbols(self):
        """
        Сканирует все активы с расширенными условиями.
        """
        symbols = self.get_all_symbols()
        print(f"Сканирование {len(symbols)} активов на паттерн Inverted Hammer")
        
        results = []
        for symbol in symbols:
            try:
                df = self.get_historical_candles(symbol, interval="60", limit=6)
                if self.check_inverted_hammer(df):
                    # Добавляем дополнительную аналитику
                    trend_strength = self.calculate_trend_strength(df)
                    results.append({
                        "symbol": symbol,
                        "trend_strength": trend_strength,
                        "volume_ratio": df["volume"].iloc[5] / df["volume"].iloc[:5].mean()
                    })
                    pass
            
            except Exception as e:
                print(f"Ошибка при обработке {symbol}: {str(e)[:50]}...")
                continue

        if results:
            print("\nНайденные паттерны Inverted Hammer")
            results_df = pd.DataFrame(results).sort_values("volume_ratio", ascending=False)
            a=(results_df.to_string(index=False))
            return a
        else:
            print("\nПаттерн Inverted Hammer не обнаружен ни на одном активе.")

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
    scanner = EnhancedInvertedHammerScanner()
    scanner.run()