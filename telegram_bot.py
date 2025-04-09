from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

import patterns.Bear
import arbitrage
import patterns.Down

TOKEN = ""

# Функции, которые выполняются в зависимости от выбора
async def execute_long(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔹 Вы выбрали LONG. Выполняю стратегию покупки, я пока еще медленный, прошу подождать 3 минуты...")

async def execute_short(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔹 Вы выбрали SHORT. Выполняю стратегию продажи,я пока еще медленный, прошу подождать 3 минуты...")
    patterns.Down.DownSignals.bearish_harami()

async def execute_arbitrage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔹 Вы выбрали АРБИТРАЖ. Ищу возможности для арбитража,я пока еще медленный, прошу подождать 3 минуты...")

# Обработка команд
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Отправь мне:\n"
        "✅ **Long** — для стратегии покупки\n"
        "✅ **Short** — для стратегии продажи\n"
        "✅ **Арбитраж** — для поиска арбитражных сделок"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower().strip()  # Удаляем лишние пробелы
    
    if text == "long":
        await execute_long(update, context)
    elif text == "short":
        await execute_short(update, context)
    elif text == "арбитраж":
        await execute_arbitrage(update, context)
    else:
        await update.message.reply_text("❌ Ошибка! Допустимые варианты: Long, Short, Арбитраж")

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    app.run_polling()

if __name__ == "__main__":
    main()