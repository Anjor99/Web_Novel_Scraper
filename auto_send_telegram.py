import os
import time
import requests
from config import Config

# ------------------ CONFIG ------------------
cfg = Config()

def get_pdfs():
    return set(f for f in os.listdir(cfg.OUTPUT_DIR) if f.lower().endswith(".pdf"))

def send_file(file_path, retries=3):
    url = f"https://api.telegram.org/bot{cfg.BOT_TOKEN}/sendDocument"
    for attempt in range(1, retries + 1):
        try:
            with open(file_path, "rb") as f:
                files = {"document": f}
                data = {"chat_id": cfg.CHAT_ID, "caption": os.path.basename(file_path)}
                r = requests.post(url, files=files, data=data, timeout=120)
            if r.status_code == 200:
                print(f"📤 Sent {file_path}")
                return
            else:
                print(f"❌ Send failed (attempt {attempt}):", r.text)
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Attempt {attempt} failed: {e}")
        time.sleep(5)
    print(f"❌ Failed to send {file_path} after {retries} attempts")


known_pdfs = get_pdfs()

print("🟢 Monitoring folder for new PDFs...")

while True:
    current_pdfs = get_pdfs()
    new_pdfs = current_pdfs - known_pdfs
    for pdf in new_pdfs:
        path = os.path.join(cfg.OUTPUT_DIR, pdf)
        print("📦 New PDF detected:", pdf)
        send_file(path)
    known_pdfs = current_pdfs
    time.sleep(cfg.CHECK_OUTPUT_INTERVAL)
