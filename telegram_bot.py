import asyncio
import sys
from pathlib import Path
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Импортируем модули из папки patterns
from patterns.Down import DownSignals
from patterns.Long import LongSignals
import arbitrage

TOKEN = "8164995862:AAF0M7eCOyo3UzfngWdqR_beltZz5E9aQXk"


async def execute_short(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка команды Short - выполняет модуль Down.py"""
    await update.message.reply_text("🔍 Запускаю сканирование медвежьих паттернов...")
    try:
        down = DownSignals()
        results = await asyncio.gather(
            down.bearish_harami(),
            down.bearish_engulfing(),
            down.falling_stars(),
            down.bearish_harami_cross()
        )
        
        response = f"📈 Результаты сканирования бычьих паттернов:\n\n"
        for i, result in enumerate(results, 1):
            await update.message.reply_text(f"Результат {i}: {result}")
        #patterns = ["Bearish Harami", "Bearish Engulfing", "Falling Stars", "Bearish Harami Cross"]
        
        # for pattern, result in zip(patterns, results):
        #     response += f"{pattern}: {len(result)} сигналов\n"
        #     if result:
        #         for i, item in enumerate(result[:3], 1):
        #             response += f"  {i}. {item.get('symbol', 'N/A')}\n"
        #     response += "\n"
        #await update.message.reply_text(response)
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")


async def execute_long(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка команды Long - выполняет модуль Long.py"""
    await update.message.reply_text("🔍 Запускаю сканирование бычьих паттернов...")
    try:
        long = LongSignals()
        results = await asyncio.gather(
            long.bullish_harami(),
            long.hammer(),
            long.inverted_hammer(),
            long.bullish_engufling(),
            long.bullish_window(),
            long.bullish_newLaws()
        )
        
        response = f"📈 Результаты сканирования бычьих паттернов:\n\n"
        for i, result in enumerate(results, 1):
            await update.message.reply_text(f"Результат {i}: {result}")
       # patterns = [
            #"Bullish Harami", "Hammer", "Inverted Hammer",
            #"Bullish Engulfing", "Bullish Window", "8-10 New Laws"
        #]
        
        # for pattern, result in zip(patterns, results):
        #     response += f"{pattern}: {len(result)} сигналов\n"
        #     if result:
        #         for i, item in enumerate(result[:2], 1):
        #             response += f"  {i}. {item.get('symbol', 'N/A')}\n"
        #     response += "\n"
        
        #await update.message.reply_text(response)
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")


async def execute_arbitrage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка команды Арбитраж"""
    await update.message.reply_text("🔍 Ищу арбитражные возможности...")
    try:
        result = await arbitrage.main()
        
        # response = "🔄 Результаты арбитража:\n\n"
        # if result:
        #     for i, item in enumerate(result[:5], 1):
        #         response += f"{i}. {item}\n"
        # else:
        #     response += "Нет арбитражных возможностей"
        
        update.message.reply_text(result)
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка команды /start"""
    await update.message.reply_text(
        "Отправьте команду:\n"
        "• Long - бычьи паттерны\n"
        "• Short - медвежьи паттерны\n"
        "• Арбитраж - поиск арбитража"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений"""
    text = update.message.text.lower().strip()
    
    if text == "short":
        await execute_short(update, context)
    elif text == "long":
        await execute_long(update, context)
    elif text == "арбитраж":
        await execute_arbitrage(update, context)
    else:
        await update.message.reply_text("❌ Используйте: Long, Short, Арбитраж")


def main():
    """Запуск бота"""
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()


if __name__ == "__main__":
    main()