import os
import subprocess
import time

from registry.novel_registry import get_all_novels
from utils.validator import validate_range
from utils.logger import logger

NOVELS = {n["title"]: n for n in get_all_novels()}


def select_novel(title):
    n = NOVELS[title]
    msg = f"📖 {title}\n"
    if n["total_chapters"]:
        msg += f"Total chapters: {n['total_chapters']}\n"
    msg += "Send start chapter"
    return msg


def set_start(title, start):
    return f"Start chapter set to {start}. Send end chapter."


def set_end(title, start, end, user_id=None):
    novel = NOVELS[title]

    # ✅ validate BEFORE starting job
    validate_range(start, end, novel.get("total_chapters"))

    job_id = int(time.time())

    env = os.environ.copy()
    env["BASE_URL"] = novel["slug"]
    env["START_CHAPTER"] = str(start)
    env["END_CHAPTER"] = str(end)
    env["JOB_ID"] = str(job_id)
    env["NOVEL_TITLE"] = title

    if user_id is not None:
        env["USER_ID"] = str(user_id)

    logger.info(
        f"[JOB {job_id}] Starting job for '{title}' "
        f"({start} → {end})"
    )

    process = subprocess.Popen(
        ["python", "-m", "scraper.chapter_scraper"],
        env=env,
        stdout=open("logs/scraper.log", "a"),
        stderr=open("logs/scraper_error.log", "a")
    )

    logger.info(
        f"[JOB {job_id}] Spawned scraper PID={process.pid}"
    )

    return (
        f"✅ Job `{job_id}` started for *{title}*\n"
        f"Chapters: {start} → {end}\n"
        f"You’ll receive the PDF when it’s ready."
    )
