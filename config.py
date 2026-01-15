from dotenv import dotenv_values

# ------------------ CONFIG ------------------
env = dotenv_values(".env")

class Config:
    BASE_URL = env.get("BASE_URL")
    START_CHAPTER = int(env.get("START_CHAPTER", 1450))
    END_CHAPTER = int(env.get("END_CHAPTER", 1700))
    CHAPTERS_PER_PDF = int(env.get("CHAPTERS_PER_PDF", 50))
    OUTPUT_DIR = env.get("OUTPUT_DIR", "outputs")
    BOT_TOKEN = env.get("BOT_TOKEN", "")
    CHAT_ID = env.get("CHAT_ID", "")
    CHECK_OUTPUT_INTERVAL = int(env.get("CHECK_INTERVAL", 5))  # seconds