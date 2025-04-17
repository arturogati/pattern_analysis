import requests
import pandas as pd
import numpy as np

class FallingStarScanner:
    def __init__(self):
        """
        Инициализация класса FallingStarScanner.
        """
        self.base_url = "https://api.bybit.com/v5/market"
        self.min_volume_ratio = 1.3  # Минимальное соотношение объема
        self.min_shadow_ratio = 2.0  # Минимальное соотношение верхней тени к телу

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

    def is_falling_star(self, candle, prev_trend):
        """
        Проверяет, является ли свеча паттерном Falling Star.
        """
        # Свеча должна быть красной (медвежьей)
        if candle['close'] >= candle['open']:
            return False
            
        body_size = abs(candle['close'] - candle['open'])
        upper_shadow = candle['high'] - max(candle['open'], candle['close'])
        lower_shadow = min(candle['open'], candle['close']) - candle['low']
        
        # Основные условия Falling Star
        has_small_body = body_size <= (candle['high'] - candle['low']) * 0.3
        has_long_upper_shadow = upper_shadow >= self.min_shadow_ratio * body_size
        has_small_lower_shadow = lower_shadow <= body_size * 0.5
        
        # Дополнительное условие - закрытие в нижней половине диапазона
        closes_in_lower_half = candle['close'] < (candle['high'] + candle['low']) / 2
        
        return has_small_body and has_long_upper_shadow and has_small_lower_shadow and closes_in_lower_half

    def check_falling_star_pattern(self, df):
        """
        Проверяет условия для надежного паттерна Falling Star:
        1. Восходящий тренд перед паттерном (4 из 5 свечей зеленые)
        2. Последняя свеча - Falling Star
        3. Подтверждение объема (объем выше среднего)
        """
        if len(df) < 6:
            return False

        # 1. Проверка восходящего тренда
        prev_candles = df.iloc[:5]
        green_count = sum(prev_candles['close'] > prev_candles['open'])
        if green_count < 4:  # Минимум 4 из 5 свечей должны быть зелеными
            return False

        # 2. Проверка последней свечи на Falling Star
        last_candle = df.iloc[5]
        if not self.is_falling_star(last_candle, green_count/5):
            return False

        # 3. Проверка объема (объем должен быть выше среднего)
        if last_candle['volume'] < self.min_volume_ratio * df['avg_volume'].iloc[5]:
            return False

        return True

    def scan_all_symbols(self):
        """
        Сканирует все активы на паттерн Falling Star.
        """
        symbols = self.get_all_symbols()
        print(f"Сканирование {len(symbols)} активов на паттерн Falling Star (6 свечей)...")
        
        results = []
        for symbol in symbols:
            try:
                df = self.get_historical_candles(symbol, interval="60", limit=6)
                if self.check_falling_star_pattern(df):
                    # Расчет дополнительных параметров
                    trend_strength = sum(df.iloc[i]['close'] > df.iloc[i]['open'] for i in range(5))/5
                    volume_ratio = df.iloc[5]['volume'] / df['avg_volume'].iloc[5]
                    star_size = (df.iloc[5]['high'] - df.iloc[5]['low'])/df.iloc[5]['low']*100
                    
                    results.append({
                        "symbol": symbol,
                        "trend_strength": f"{trend_strength:.0%}",
                        "volume_ratio": f"{volume_ratio:.1f}x",
                        "star_size": f"{star_size:.2f}%",
                        "close_price": df.iloc[5]['close']
                    })
            
            except Exception as e:
                print(f"Ошибка при обработке {symbol}: {str(e)[:50]}...")
                continue

        if results:
            print("\nНайденные паттерны Falling Star:")
            results_df = pd.DataFrame(results).sort_values("volume_ratio", ascending=False)
            a=(results_df.to_string(index=False))
            #a=results[0]['symbol']
            return a
        else:
            print("\nПаттерн Falling Star не найден ни на одном активе.")

    def run(self):
        self.scan_all_symbols()

if __name__ == "__main__":
    scanner = FallingStarScanner()
    scanner.run()