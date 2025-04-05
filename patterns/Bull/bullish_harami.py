import requests
import pandas as pd
import numpy as np

class BullishHaramiScanner:
    def __init__(self):
        """
        Инициализация класса BullishHaramiScanner.
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

    def is_bullish_harami(self, first_candle, second_candle):
        """
        Проверяет, является ли комбинация свечей паттерном Bullish Harami.
        """
        # Первая свеча должна быть красной (медвежьей)
        if first_candle['close'] >= first_candle['open']:
            return False
            
        # Вторая свеча должна быть зеленой (бычьей)
        if second_candle['close'] <= second_candle['open']:
            return False
            
        # Тело второй свечи должно быть полностью внутри тела первой свечи
        harami_condition = (second_candle['open'] > first_candle['close']) and \
                          (second_candle['close'] < first_candle['open'])
        
        return harami_condition

    def check_bullish_harami_pattern(self, df):
        """
        Проверяет условия для надежного паттерна Bullish Harami:
        1. Предшествующий нисходящий тренд (4 из 5 свечей красные)
        2. Последние две свечи образуют Bullish Harami
        3. Подтверждение объема (объем выше среднего)
        """
        if len(df) < 6:
            return False

        # 1. Проверка нисходящего тренда
        prev_candles = df.iloc[:4]  # Свечи перед паттерном
        red_count = sum(prev_candles['close'] < prev_candles['open'])
        if red_count < 3:  # Минимум 3 из 4 свечей должны быть красными
            return False

        # 2. Проверка последних двух свечей на Bullish Harami
        first_candle = df.iloc[4]  # Первая свеча паттерна
        second_candle = df.iloc[5]  # Вторая свеча паттерна
        
        if not self.is_bullish_harami(first_candle, second_candle):
            return False

        # 3. Проверка объема
        if second_candle['volume'] < self.min_volume_ratio * df['avg_volume'].iloc[5]:
            return False

        return True

    def scan_all_symbols(self):
        """
        Сканирует все активы на паттерн Bullish Harami.
        """
        symbols = self.get_all_symbols()
        print(f"Сканирование {len(symbols)} активов на паттерн Bullish Harami")
        
        results = []
        for symbol in symbols:
            try:
                df = self.get_historical_candles(symbol, interval="60", limit=6)
                if self.check_bullish_harami_pattern(df):
                    # Расчет дополнительных параметров
                    trend_strength = sum(df.iloc[i]['close'] < df.iloc[i]['open'] for i in range(4))/4
                    volume_ratio = df.iloc[5]['volume'] / df['avg_volume'].iloc[5]
                    harami_size = (df.iloc[4]['open'] - df.iloc[4]['close'])/df.iloc[4]['close']*100
                    
                    results.append({
                        "symbol": symbol,
                        "trend_strength": f"{trend_strength:.0%}",
                        "volume_ratio": f"{volume_ratio:.1f}x",
                        "harami_size": f"{harami_size:.2f}%",
                        "close_price": df.iloc[5]['close']
                    })
            
            except Exception as e:
                print(f"Ошибка при обработке {symbol}: {str(e)[:50]}...")
                continue

        if results:
            print("\nНайденные паттерны Bullish harami:")
            results_df = pd.DataFrame(results).sort_values("volume_ratio", ascending=False)
            print(results_df.to_string(index=False))
        else:
            print("\nПаттерн Bullish Harami не найден ни на одном активе.")

    def run(self):
        self.scan_all_symbols()

if __name__ == "__main__":
    scanner = BullishHaramiScanner()
    scanner.run()