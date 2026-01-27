import os
import time
import requests
from config.settings import Config
from utils.logger import logger

cfg = Config()


def get_pdfs():
    return {
        f for f in os.listdir(cfg.OUTPUT_DIR)
        if f.lower().endswith(".pdf")
    }


def parse_filename(filename):
    """
    Expected format:
    <chat_id>__<novel>_<start>_to_<end>.pdf
    """
    try:
        chat_part, rest = filename.split("__", 1)
        return chat_part, rest
    except ValueError:
        return None, None


def send_file(chat_id, file_path, display_name, retries=3):
    url = f"https://api.telegram.org/bot{cfg.BOT_TOKEN}/sendDocument"

    for attempt in range(1, retries + 1):
        try:
            with open(file_path, "rb") as f:
                files = {"document": (display_name, f)}
                data = {"chat_id": chat_id, "caption": display_name}

                r = requests.post(
                    url,
                    files=files,
                    data=data,
                    timeout=(10, 180),
                    headers={"Connection": "close"}
                )

            if r.status_code == 200:
                logger.info(f"📤 Sent to chat {chat_id}: {display_name}")
                return True
            else:
                logger.error(f"❌ Send failed (attempt {attempt}): {r.text}")

        except requests.exceptions.RequestException as e:
            logger.error(f"⚠️ Attempt {attempt} failed: {e}")

        time.sleep(8)   # slower retry

    return False

def process_existing_pdfs():
    logger.info("🔄 Processing existing PDFs on startup...")

    for pdf in get_pdfs():
        full_path = os.path.join(cfg.OUTPUT_DIR, pdf)
        chat_id, original_name = parse_filename(pdf)

        if not chat_id:
            logger.warning(f"⚠️ Skipping unrecognized file: {pdf}")
            continue

        display_name = "novel_" + original_name.split("_", 1)[-1]

        logger.info(
            f"📦 Found pending PDF for chat {chat_id}: {display_name}"
        )

        success = send_file(
            chat_id=chat_id,
            file_path=full_path,
            display_name=display_name
        )

        if success:
            os.remove(full_path)
            logger.info(f"🗑️ Deleted sent file: {pdf}")

process_existing_pdfs()

known_pdfs = set()
logger.info("🟢 Monitoring folder for new PDFs...")

while True:
    current_pdfs = get_pdfs()
    new_pdfs = current_pdfs - known_pdfs

    for pdf in new_pdfs:
        full_path = os.path.join(cfg.OUTPUT_DIR, pdf)
        chat_id, original_name = parse_filename(pdf)

        if not chat_id:
            logger.warning(f"⚠️ Skipping unrecognized file: {pdf}")
            continue

        display_name = "novel_" + original_name.split("_", 1)[-1]

        logger.info(
            f"📦 New PDF detected for chat {chat_id}: {display_name}"
        )

        sending_path = full_path + ".sending"
        os.rename(full_path, sending_path)

        success = send_file(
            chat_id=chat_id,
            file_path=sending_path,
            display_name=display_name
        )

        if success:
            os.remove(sending_path)
            logger.info(f"🗑️ Deleted sent file: {pdf}")


    known_pdfs = current_pdfs
    time.sleep(cfg.CHECK_OUTPUT_INTERVAL)
