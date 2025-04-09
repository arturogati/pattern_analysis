import Bear
import asyncio

import Bear.Bearish_engulfing
import Bear.Bearish_harami
import Bear.Bearish_harami_cross
import Bear.Falling_stars


class DownSignals:
    async def bearish_harami(self):
        """
        Асинхронная функция для поиска паттерна Bearish Harami.
        """
        scanner = Bear.Bearish_harami.BearishHaramiScanner()
        # Запускаем сканирование всех активов
        await asyncio.to_thread(scanner.scan_all_symbols)

    async def bearish_engulfing(self):
        """
        Асинхронная функция для поиска паттерна bearish engulfing.
        """
        scanner = Bear.Bearish_engulfing.BearishEngulfingScanner()
        # Запускаем сканирование всех активов
        await asyncio.to_thread(scanner.scan_all_symbols)

    async def falling_stars(self):
        """
        Асинхронная функция для поиска паттерна Falling Stars.
        """
        scanner = Bear.Falling_stars.FallingStarScanner()
        # Запускаем сканирование всех активов
        await asyncio.to_thread(scanner.scan_all_symbols)

    async def bearish_harami_cross(self):
        """
        Асинхронная функция для поиска паттерна bearish harami cross.
        """
        scanner = Bear.Bearish_harami_cross.BearishHaramiCrossScanner()
        # Запускаем сканирование всех активов
        await asyncio.to_thread(scanner.scan_all_symbols)

        

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