from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import patterns.Down
import patterns.Long
import arbitrage.main
import arbitrage
import asyncio

TOKEN = ""

async def execute_short(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Вызывает patterns.Down и отправляет результаты."""
    await update.message.reply_text("🔍 Запускаю сканирование медвежьих паттернов (Down)...")
    try:
        result = await patterns.Down().main()  # Предполагаем, что метод main() есть в patterns.Down
        await update.message.reply_text(f"📉 **Результаты (Short):**\n\n{result}")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

async def execute_long(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Вызывает patterns.Long и отправляет результаты."""
    await update.message.reply_text("🔍 Запускаю сканирование бычьих паттернов (Long)...")
    try:
        result = await patterns.Long().main()  # Предполагаем, что метод main() есть в patterns.Long
        await update.message.reply_text(f"📈 **Результаты (Long):**\n\n{result}")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

async def execute_arbitrage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Вызывает arbitrage.main и отправляет результаты."""
    await update.message.reply_text("🔍 Ищу арбитражные возможности...")
    try:
        result = await arbitrage.main()  # Предполагаем, что arbitrage.main() корутина
        await update.message.reply_text(f"🔄 **Результаты (Арбитраж):**\n\n{result}")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Приветственное сообщение."""
    await update.message.reply_text(
        "Отправьте команду:\n"
        "• **Long** — бычьи паттерны\n"
        "• **Short** — медвежьи паттерны\n"
        "• **Арбитраж** — поиск арбитража"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых команд."""
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
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()