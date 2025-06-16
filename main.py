import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

BOT_TOKEN = os.getenv("BOT_TOKEN")

ASK_NAME, ASK_CONTACT, ASK_INTEREST, ASK_COMMENT = range(4)

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот проекта «Деньги без Людей». Давайте начнём. Как вас зовут?")
    return ASK_NAME

async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Отлично! Как с вами можно связаться? (Telegram @username или номер)")
    return ASK_CONTACT

async def ask_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["contact"] = update.message.text
    await update.message.reply_text("Что вам интересно? (AI / партнёрки / обучение и т.д.)")
    return ASK_INTEREST

async def ask_interest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["interest"] = update.message.text
    await update.message.reply_text("Коротко напишите, с чем хотите разобраться или что бы хотели получить.")
    return ASK_COMMENT

async def ask_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["comment"] = update.message.text

    # Подтверждение
    summary = f"""
Заявка принята ✅

👤 Имя: {context.user_data['name']}
📱 Контакт: {context.user_data['contact']}
💡 Интерес: {context.user_data['interest']}
📝 Комментарий: {context.user_data['comment']}
"""
    await update.message.reply_text(summary + "\nСпасибо! Мы свяжемся с вами в ближайшее время.")

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отменено.")
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)],
            ASK_CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_contact)],
            ASK_INTEREST: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_interest)],
            ASK_COMMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_comment)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == '__main__':
    main()
