import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters
from scraper import fetch_chapter, build_pdf
from config import Config

cfg = Config()

# ------------------ Logging ------------------
logging.basicConfig(level=logging.INFO)

# ------------------ Error handler ------------------
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.error(f"Exception while handling an update: {context.error}")

# ------------------ Bot Conversation states ------------------
SELECT_FROM, SELECT_TO = range(2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hi! Enter the start chapter number:")
    return SELECT_FROM

async def select_from(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text.isdigit():
        await update.message.reply_text("❌ Please enter a valid number for the start chapter.")
        return SELECT_FROM
    context.user_data['start_ch'] = int(text)
    await update.message.reply_text(f"Start chapter set to {text}. Now enter the end chapter:")
    return SELECT_TO

async def select_to(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text.isdigit():
        await update.message.reply_text("❌ Please enter a valid number for the end chapter.")
        return SELECT_TO
    start_ch = context.user_data['start_ch']
    end_ch = int(text)
    if end_ch < start_ch:
        await update.message.reply_text("❌ End chapter must be greater than start chapter. Try again.")
        return SELECT_TO

    await update.message.reply_text(f"📦 Generating PDF for chapters {start_ch} to {end_ch}...")

    chapters = []
    for ch in range(start_ch, end_ch + 1):
        try:
            chapters.append(fetch_chapter(ch))
        except Exception as e:
            chapters.append((f"Chapter {ch} - Failed", [f"⚠️ Could not fetch chapter {ch}. URL: {cfg.BASE_URL}{ch}"]))

    output_file = f"{cfg.OUTPUT_DIR}/Dynamic_{start_ch}_to_{end_ch}.pdf"
    build_pdf(chapters, start_ch, end_ch)

    await update.message.reply_document(document=open(output_file, "rb"), filename=os.path.basename(output_file))
    await update.message.reply_text("✅ PDF sent!")

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Operation cancelled.")
    return ConversationHandler.END

# ------------------ Main ------------------
def main():
    os.makedirs(cfg.OUTPUT_DIR, exist_ok=True)

    # Create the bot application
    app = ApplicationBuilder().token(cfg.BOT_TOKEN).build()

    # Add the conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SELECT_FROM: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_from)],
            SELECT_TO: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_to)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    app.add_handler(conv_handler)

    # ------------------ Add the error handler here ------------------
    app.add_error_handler(error_handler)

    # Run the bot
    app.run_polling()

if __name__ == "__main__":
    main()
