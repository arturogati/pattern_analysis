import requests
import pandas as pd
import numpy as np

class HammerPatternScanner:
    def __init__(self):
        """
        Инициализация класса HammerPatternScanner.
        """
        self.base_url = "https://api.bybit.com/v5/market"
        self.min_volume_ratio = 1.2  # Минимальное соотношение объема

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

    def is_hammer(self, candle):
        """
        Проверяет, является ли свеча паттерном Hammer.
        """
        body_size = abs(candle['close'] - candle['open'])
        upper_shadow = candle['high'] - max(candle['open'], candle['close'])
        lower_shadow = min(candle['open'], candle['close']) - candle['low']
        
        # Основные условия Hammer
        small_body = body_size <= (candle['high'] - candle['low']) * 0.3
        long_lower_shadow = lower_shadow >= 2 * body_size
        small_upper_shadow = upper_shadow <= body_size * 0.5
        
        return small_body and long_lower_shadow and small_upper_shadow

    def check_hammer_pattern(self, df):
        """
        Проверяет условия для надежного паттерна Hammer:
        1. Предшествующий нисходящий тренд (4 из 5 свечей красные)
        2. Последняя свеча - Hammer
        3. Подтверждение объема (объем выше среднего)
        """
        if len(df) < 6:
            return False

        # 1. Проверка нисходящего тренда
        prev_candles = df.iloc[:5]
        red_count = sum(prev_candles['close'] < prev_candles['open'])
        if red_count < 4:
            return False

        # 2. Проверка последней свечи на Hammer
        last_candle = df.iloc[5]
        if not self.is_hammer(last_candle):
            return False

        # 3. Проверка объема
        if last_candle['volume'] < self.min_volume_ratio * df['avg_volume'].iloc[5]:
            return False

        return True

    def scan_all_symbols(self):
        """
        Сканирует все активы на паттерн Hammer.
        """
        symbols = self.get_all_symbols()
        print(f"Сканирование {len(symbols)} активов на паттерн Hammer (6 свечей)...")
        
        results = []
        for symbol in symbols:
            try:
                df = self.get_historical_candles(symbol, interval="60", limit=6)
                if self.check_hammer_pattern(df):
                    # Расчет дополнительных параметров
                    trend_strength = sum(df.iloc[i]['close'] < df.iloc[i]['open'] for i in range(5))/5
                    volume_ratio = df.iloc[5]['volume'] / df['avg_volume'].iloc[5]
                    hammer_size = (df.iloc[5]['high'] - df.iloc[5]['low']) / df.iloc[5]['low'] * 100
                    
                    results.append({
                        "symbol": symbol,
                        "trend_strength": f"{trend_strength:.0%}",
                        "volume_ratio": f"{volume_ratio:.1f}x",
                        "hammer_size": f"{hammer_size:.2f}%"
                    })
            
            except Exception as e:
                print(f"Ошибка при обработке {symbol}: {str(e)[:50]}...")
                continue

        if results:
            print("\nНайденные паттерны Hammer:")
            results_df = pd.DataFrame(results)
            print(results_df.to_string(index=False))
        else:
            print("\nПаттерн Hammer не найден ни на одном активе.")

    def run(self):
        self.scan_all_symbols()

if __name__ == "__main__":
    scanner = HammerPatternScanner()
    scanner.run()