import Bull
import Bull.bullish_engufling
import Bull.bullish_engufling
import Bull.bullish_harami
import Bull.bullish_window
import Bull.hammer
import Bull.new_laws
import asyncio

import Bull.inverted_hammer


class LongSignals:
    async def bullish_harami(self):
        """
        Асинхронная функция для поиска паттерна Bullish Harami.
        """
        scanner = Bull.bullish_harami.BullishHaramiScanner()
        # Запускаем сканирование всех активов
        await asyncio.to_thread(scanner.scan_all_symbols)

    async def hammer(self):
        """
        Асинхронная функция для поиска паттерна Hammer.
        """
        scanner = Bull.hammer.HammerPatternScanner()
        # Запускаем сканирование всех активов
        await asyncio.to_thread(scanner.scan_all_symbols)

    async def inverted_hammer(self):
        """
        Асинхронная функция для поиска паттерна InvertedHammer.
        """
        scanner = Bull.inverted_hammer.EnhancedInvertedHammerScanner()
        # Запускаем сканирование всех активов
        await asyncio.to_thread(scanner.scan_all_symbols)

    async def bullish_engufling(self):
        """
        Асинхронная функция для поиска паттерна Bullish engufling .
        """
        scanner = Bull.bullish_engufling.BullishEngulfingScanner()
        # Запускаем сканирование всех активов
        await asyncio.to_thread(scanner.scan_all_symbols)

    async def bullish_window(self):
        """
        Асинхронная функция для поиска паттерна Bullish effort .
        """
        scanner = Bull.bullish_window.EnhancedBullishWindowScanner()
        # Запускаем сканирование всех активов
        await asyncio.to_thread(scanner.scan_all_symbols)

    async def bullish_newLaws(self):
        """
        Асинхронная функция для поиска паттерна 8-10 New Laws.
        """
        scanner = Bull.new_laws.NewLawsScanner()
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
        long_signals.inverted_hammer(),
        long_signals.bullish_engufling(),
        long_signals.bullish_window(),
        long_signals.bullish_newLaws()
    )

# Запуск асинхронного кода
if __name__ == "__main__":
    asyncio.run(main())
    