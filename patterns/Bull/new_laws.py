import requests
import pandas as pd
import numpy as np

class NewLawsScanner:
    def __init__(self):
        """
        Инициализация класса NewLawsScanner.
        """
        self.base_url = "https://api.bybit.com/v5/market"
        self.min_volume_ratio = 1.3  # Минимальное соотношение объема для подтверждения

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

    def get_historical_candles(self, symbol, interval="60", limit=11):
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
        
        # Добавляем скользящие средние
        df['volume_ma'] = df['volume'].rolling(window=10).mean()
        df['close_ma'] = df['close'].rolling(window=10).mean()
        
        return df

    def check_new_laws_pattern(self, df):
        """
        Проверяет условия для паттерна 8-10 New Laws:
        1. 8-10 красных свечей подряд (нисходящий тренд)
        2. Последняя свеча зеленая (разворотная)
        3. Увеличение объема на разворотной свече
        4. Цена закрытия выше 10-периодного MA
        """
        if len(df) < 11:
            return False

        # 1. Проверка 8-10 красных свечей
        red_candles = sum(df.iloc[i]['close'] < df.iloc[i]['open'] for i in range(10))
        if red_candles < 8 or red_candles > 10:
            return False

        # 2. Последняя свеча должна быть зеленой
        last_candle = df.iloc[10]
        if last_candle['close'] <= last_candle['open']:
            return False

        # 3. Проверка объема (должен быть выше среднего)
        if last_candle['volume'] < self.min_volume_ratio * df['volume_ma'].iloc[10]:
            return False

        # 4. Цена закрытия выше 10-периодного MA
        if last_candle['close'] <= df['close_ma'].iloc[10]:
            return False

        return True

    def scan_all_symbols(self):
        """
        Сканирует все активы на паттерн 8-10 New Laws.
        """
        symbols = self.get_all_symbols()
        print(f"Сканирование {len(symbols)} активов на паттерн 8-10 New Laws (11 свечей)...")
        
        results = []
        for symbol in symbols:
            try:
                df = self.get_historical_candles(symbol, interval="60", limit=11)
                if self.check_new_laws_pattern(df):
                    # Расчет дополнительных параметров
                    red_count = sum(df.iloc[i]['close'] < df.iloc[i]['open'] for i in range(10))
                    volume_ratio = df.iloc[10]['volume'] / df['volume_ma'].iloc[10]
                    price_change = (df.iloc[10]['close'] - df.iloc[0]['close'])/df.iloc[0]['close']*100
                    
                    results.append({
                        "symbol": symbol,
                        "red_candles": red_count,
                        "volume_ratio": f"{volume_ratio:.1f}x",
                        "price_change": f"{price_change:.2f}%",
                        "close_price": df.iloc[10]['close']
                    })
            
            except Exception as e:
                print(f"Ошибка при обработке {symbol}: {str(e)[:50]}...")
                continue

        if results:
            print("\nНайденные паттерны 8-10 New Laws:")
            results_df = pd.DataFrame(results).sort_values("volume_ratio", ascending=False)
            print(results_df.to_string(index=False))
        else:
            print("\nПаттерн 8-10 New Laws не найден ни на одном активе.")

    def run(self):
        self.scan_all_symbols()

if __name__ == "__main__":
    scanner = NewLawsScanner()
    scanner.run()