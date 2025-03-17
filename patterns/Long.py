import Bull
import Bull.bullish_harami
import Bull.hammer
import asyncio

import Bull.inverted_hammer


class LongSignals:
    async def bullish_harami(self):
        """
        Асинхронная функция для поиска паттерна Bullish Harami.
        """
        scanner = Bull.bullish_harami.BullishHarami()
        # Запускаем сканирование всех активов
        await asyncio.to_thread(scanner.scan_all_symbols)

    async def hammer(self):
        """
        Асинхронная функция для поиска паттерна Hammer.
        """
        scanner = Bull.hammer.HammerPattern()
        # Запускаем сканирование всех активов
        await asyncio.to_thread(scanner.scan_all_symbols)

    async def inverted_hammer(self):
        """
        Асинхронная функция для поиска паттерна InvertedHammer.
        """
        scanner = Bull.inverted_hammer.InvertedHammer()
        # Запускаем сканирование всех активов
        await asyncio.to_thread(scanner.scan_all_symbols)

        

async def main():
    """
    Основная асинхронная функция для запуска задач.
    """
    # Создаем объект класса LongSignals
    long_signals = LongSignals()
    
    # Запускаем обе функции асинхронно
    await asyncio.gather(
        long_signals.bullish_harami(),
        long_signals.hammer(),
        long_signals.inverted_hammer()
    )

# Запуск асинхронного кода
if __name__ == "__main__":
    asyncio.run(main())
    