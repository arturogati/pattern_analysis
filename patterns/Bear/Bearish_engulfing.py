import requests
import pandas as pd
import numpy as np

class BearishEngulfingScanner:
    def __init__(self):
        """
        Инициализация класса BearishEngulfingScanner.
        """
        self.base_url = "https://api.bybit.com/v5/market"
        self.min_volume_ratio = 1.5  # Минимальное соотношение объема для подтверждения

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
        
        # Добавляем скользящее среднее объема
        df['avg_volume'] = df['volume'].rolling(window=5).mean()
        
        return df

    def is_bearish_engulfing(self, first_candle, second_candle):
        """
        Проверяет, является ли комбинация свечей паттерном Bearish Engulfing.
        """
        # Первая свеча должна быть зеленой (бычьей)
        if first_candle['close'] <= first_candle['open']:
            return False
            
        # Вторая свеча должна быть красной (медвежьей)
        if second_candle['close'] >= second_candle['open']:
            return False
            
        # Тело второй свечи должно полностью поглощать тело первой свечи
        engulfing_condition = (second_candle['open'] > first_candle['close']) and \
                             (second_candle['close'] < first_candle['open'])
        
        return engulfing_condition

    def check_bearish_engulfing_pattern(self, df):
        """
        Проверяет условия для надежного паттерна Bearish Engulfing:
        1. Предшествующий восходящий тренд (4 из 5 свечей зеленые)
        2. Последние две свечи образуют Bearish Engulfing
        3. Подтверждение объема (объем выше среднего)
        4. Цена закрытия ниже EMA20 (опционально, можно добавить)
        """
        if len(df) < 6:
            return False

        # 1. Проверка восходящего тренда
        prev_candles = df.iloc[:4]  # Свечи перед паттерном
        green_count = sum(prev_candles['close'] > prev_candles['open'])
        if green_count < 3:  # Минимум 3 из 4 свечей должны быть зелеными
            return False

        # 2. Проверка последних двух свечей на Bearish Engulfing
        first_candle = df.iloc[4]  # Первая свеча паттерна (бычья)
        second_candle = df.iloc[5]  # Вторая свеча паттерна (медвежья)
        
        if not self.is_bearish_engulfing(first_candle, second_candle):
            return False

        # 3. Проверка объема (объем должен быть значительно выше среднего)
        if second_candle['volume'] < self.min_volume_ratio * df['avg_volume'].iloc[5]:
            return False

        return True

    def scan_all_symbols(self):
        """
        Сканирует все активы на паттерн Bearish Engulfing.
        """
        symbols = self.get_all_symbols()
        print(f"Сканирование {len(symbols)} активов на паттерн Bearish Engulfing (6 свечей)...")
        
        results = []
        for symbol in symbols:
            try:
                df = self.get_historical_candles(symbol, interval="60", limit=6)
                if self.check_bearish_engulfing_pattern(df):
                    # Расчет дополнительных параметров
                    trend_strength = sum(df.iloc[i]['close'] > df.iloc[i]['open'] for i in range(4))/4
                    volume_ratio = df.iloc[5]['volume'] / df['avg_volume'].iloc[5]
                    engulfing_size = (df.iloc[5]['open'] - df.iloc[5]['close'])/df.iloc[5]['open']*100
                    
                    results.append({
                        "symbol": symbol,
                        "trend_strength": f"{trend_strength:.0%}",
                        "volume_ratio": f"{volume_ratio:.1f}x",
                        "engulfing_size": f"{engulfing_size:.2f}%",
                        "close_price": df.iloc[5]['close']
                    })
            
            except Exception as e:
                print(f"Ошибка при обработке {symbol}: {str(e)[:50]}...")
                continue

        if results:
            print("\nНайденные паттерны Bearish Engulfing:")
            results_df = pd.DataFrame(results).sort_values("volume_ratio", ascending=False)
            print(results_df.to_string(index=False))
        else:
            print("\nПаттерн Bearish Engulfing не найден ни на одном активе.")

    def run(self):
        self.scan_all_symbols()

if __name__ == "__main__":
    scanner = BearishEngulfingScanner()
    scanner.run()