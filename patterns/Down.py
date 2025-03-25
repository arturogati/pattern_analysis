import Bear
import asyncio

import Bear.Bearish_harami
import Bear.Dark_storm_cloud
import Bear.Falling_stars
import Bear.new_heights

class DownSignals:
    async def bearish_harami(self):
        """
        Асинхронная функция для поиска паттерна Bearish Harami.
        """
        scanner = Bear.Bearish_harami.BearishHarami()
        # Запускаем сканирование всех активов
        await asyncio.to_thread(scanner.scan_all_symbols)

    async def dark_storm_cloud(self):
        """
        Асинхронная функция для поиска паттерна Dark Storm Cloud.
        """
        scanner = Bear.Dark_storm_cloud.DarkStormCloud()
        # Запускаем сканирование всех активов
        await asyncio.to_thread(scanner.scan_all_symbols)

    async def falling_stars(self):
        """
        Асинхронная функция для поиска паттерна Falling Stars.
        """
        scanner = Bear.Falling_stars.FallingStar()
        # Запускаем сканирование всех активов
        await asyncio.to_thread(scanner.scan_all_symbols)

    async def new_heights(self):
        """
        Асинхронная функция для поиска паттерна 8-9 new heights.
        """
        scanner = Bear.new_heights.NewHeights()
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
        down_signals.dark_storm_cloud(),
        down_signals.falling_stars(),
        down_signals.new_heights()
    )

# Запуск асинхронного кода
if __name__ == "__main__":
    asyncio.run(main())