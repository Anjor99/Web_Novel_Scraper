from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
import os
import json

from registry.novel_registry import get_all_novels
from flow.novel_flow import select_novel, set_start, set_end
from bot.state import USER_STATE
from config.settings import Config


# ------------------ SETUP ------------------

cfg = Config()
JOB_DIR = cfg.JOB_DIR
os.makedirs(JOB_DIR, exist_ok=True)

NOVELS = get_all_novels()


# ------------------ /start ------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(n["title"], callback_data=n["title"])]
        for n in NOVELS
    ]

    await update.message.reply_text(
        "📚 *Select a novel:*",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


# ------------------ NOVEL SELECT ------------------

async def novel_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    USER_STATE[query.from_user.id] = {
        "title": query.data,
        "stage": "start",
    }

    await query.message.reply_text(
        select_novel(query.data),
        parse_mode="Markdown",
    )


# ------------------ /status ------------------

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    job_id_filter = context.args[0] if context.args else None

    jobs = []

    for file in os.listdir(JOB_DIR):
        path = os.path.join(JOB_DIR, file)

        try:
            with open(path) as f:
                data = json.load(f)
        except Exception:
            # corrupted / half-written job file
            continue

        if str(data.get("chat_id")) != chat_id:
            continue

        if job_id_filter and str(data.get("job_id")) != job_id_filter:
            continue

        jobs.append(data)

    if not jobs:
        await update.message.reply_text("📭 No active jobs found.")
        return

    messages = []

    for j in jobs:
        start = j["start"]
        end = j["end"]
        current = j["current"]

        total = end - start + 1
        done = max(0, current - start + 1)
        percent = int((done / total) * 100) if total > 0 else 0

        filled = percent // 10
        bar = "█" * filled + "░" * (10 - filled)

        if j["status"] == "running":
            status_text = "⏳ In Progress"
        elif j["status"] == "completed":
            status_text = "✅ Completed"
        elif j["status"] == "failed":
            status_text = f"❌ Failed Please try again"

        if j["status"] == "failed" or j["status"] == "completed":
            # Show the failed and completed jobs once in chat and then remove the json from jobs folder
            messages.append(
                f"📖 *{j['novel']}*\n"
                f"Job: `{j['job_id']}`\n"
                f"[{bar}] {percent}%\n"
                f"Chapter {current} / {end}\n"
                f"Status: {status_text}"
            )
            os.remove(os.path.join(JOB_DIR, f"{j['job_id']}.json"))
        else:
            messages.append(
                f"📖 *{j['novel']}*\n"
                f"Job: `{j['job_id']}`\n"
                f"[{bar}] {percent}%\n"
                f"Chapter {current} / {end}\n"
                f"Status: {status_text}"
            )
            
    
    await update.message.reply_text(
        "\n\n".join(messages),
        parse_mode="Markdown",
    )


# ------------------ TEXT INPUT ------------------

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.strip()

    if user_id not in USER_STATE:
        await update.message.reply_text("❗ Use /start first")
        return

    state = USER_STATE[user_id]
    title = state["title"]

    # -------- START CHAPTER --------
    if state["stage"] == "start":
        if not text.isdigit():
            await update.message.reply_text("❌ Send a valid number")
            return

        state["start"] = int(text)
        state["stage"] = "end"

        await update.message.reply_text(
            set_start(title, state["start"])
        )
        return

    # -------- END CHAPTER --------
    if state["stage"] == "end":
        if not text.isdigit():
            await update.message.reply_text("❌ Send a valid number")
            return

        try:
            chat_id = update.effective_chat.id

            result = set_end(
                title=title,
                start=state["start"],
                end=int(text),
                user_id=chat_id,
            )

            await update.message.reply_text(result)

        except Exception as e:
            await update.message.reply_text(f"❌ {e}")
            return

        USER_STATE.pop(user_id, None)
        await update.message.reply_text(
            "📦 PDF will be sent automatically."
        )
