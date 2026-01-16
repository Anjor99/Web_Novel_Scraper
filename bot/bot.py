from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from config.settings import Config
from bot.handlers import start, novel_selected, handle_text, status

cfg = Config()


# ---------- ERROR HANDLER ----------
async def error_handler(update, context: ContextTypes.DEFAULT_TYPE):
    print("⚠️ Telegram error:", context.error)


def run_bot():
    app = ApplicationBuilder().token(cfg.BOT_TOKEN).build()

    # ---- Register handlers ----
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))  
    app.add_handler(CallbackQueryHandler(novel_selected))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # ✅ THIS LINE (you asked where)
    app.add_error_handler(error_handler)

    print("🤖 Telegram bot running...")
    app.run_polling()


if __name__ == "__main__":
    run_bot()
