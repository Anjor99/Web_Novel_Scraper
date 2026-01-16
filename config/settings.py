import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    CHAT_ID = os.getenv("CHAT_ID")

    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "outputs")
    CHECK_OUTPUT_INTERVAL = int(os.getenv("CHECK_OUTPUT_INTERVAL", 5))

    BASE_URL = os.getenv("BASE_URL")
    START_CHAPTER = int(os.getenv("START_CHAPTER", 1))
    END_CHAPTER = int(os.getenv("END_CHAPTER", 1))
    CHAPTERS_PER_PDF = int(os.getenv("CHAPTERS_PER_PDF", 50))
    JOB_DIR = os.getenv("JOB_DIR", "jobs")
