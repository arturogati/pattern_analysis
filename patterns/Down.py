import asyncio

from patterns.Bear.Bearish_engulfing import BearishEngulfingScanner
from patterns.Bear.Bearish_harami import BearishHaramiScanner
from patterns.Bear.Bearish_harami_cross import BearishHaramiCrossScanner
from patterns.Bear.Falling_stars import FallingStarScanner


class DownSignals:
    async def bearish_harami(self):
        """
        Асинхронная функция для поиска паттерна Bearish Harami.
        """
        scanner = BearishHaramiScanner()
        # Запускаем сканирование всех активов
        return await asyncio.to_thread(scanner.scan_all_symbols)

    async def bearish_engulfing(self):
        """
        Асинхронная функция для поиска паттерна bearish engulfing.
        """
        scanner = BearishEngulfingScanner()
        # Запускаем сканирование всех активов
        return await asyncio.to_thread(scanner.scan_all_symbols)

    async def falling_stars(self):
        """
        Асинхронная функция для поиска паттерна Falling Stars.
        """
        scanner = FallingStarScanner()
        # Запускаем сканирование всех активов
        return await asyncio.to_thread(scanner.scan_all_symbols)

    async def bearish_harami_cross(self):
        """
        Асинхронная функция для поиска паттерна bearish harami cross.
        """
        scanner = BearishHaramiCrossScanner()
        # Запускаем сканирование всех активов
        return await asyncio.to_thread(scanner.scan_all_symbols)

        

async def main():
    """
    Основная асинхронная функция для запуска задач.
    """
    # Создаем объект класса LongSignals
    down_signals = DownSignals()
    
    # Запускаем обе функции асинхронно
    await asyncio.gather(
        down_signals.bearish_harami(),
        down_signals.bearish_engulfing(),
        down_signals.falling_stars(),
        down_signals.bearish_harami_cross()
    )

# Запуск асинхронного кода
if __name__ == "__main__":
    asyncio.run(main())