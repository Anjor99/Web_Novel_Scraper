import os
import time
import requests
import json
from bs4 import BeautifulSoup

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from config.settings import Config
from utils.logger import logger

# ------------------ JOB METADATA ------------------

job_id = os.getenv("JOB_ID", "unknown")
novel_title = os.getenv("NOVEL_TITLE", "UnknownNovel")
chat_id = os.getenv("USER_ID", "unknown")
JOB_DIR = Config.JOB_DIR
os.makedirs(JOB_DIR, exist_ok=True)

job_file = os.path.join(JOB_DIR, f"{job_id}.json")

safe_title = "".join(
    c if c.isalnum() or c in (" ", "_") else "_"
    for c in novel_title
).replace(" ", "_")

logger.info(f"[JOB {job_id}] Scraper started")
logger.info(f"[JOB {job_id}] BASE_URL={os.getenv('BASE_URL')}")
logger.info(
    f"[JOB {job_id}] Chapters {os.getenv('START_CHAPTER')} → {os.getenv('END_CHAPTER')}"
)


# ------------------ CONFIG ------------------

cfg = Config()
os.makedirs(cfg.OUTPUT_DIR, exist_ok=True)

with open(job_file, "w") as f:
    json.dump({
        "job_id": job_id,
        "chat_id": chat_id,
        "novel": novel_title,
        "start": cfg.START_CHAPTER,
        "end": cfg.END_CHAPTER,
        "current": cfg.START_CHAPTER - 1,
        "status": "running"
    }, f)

# ------------------ SESSION (⚠️ IMPORTANT) ------------------

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) Chrome/120 Safari/537.36",
    "Referer": "https://www.freewebnovel.com/",
})


# ------------------ STYLES ------------------

styles = getSampleStyleSheet()

styles.add(ParagraphStyle(
    name="ChapterTitle",
    fontSize=16,
    leading=20,
    spaceAfter=14
))

styles.add(ParagraphStyle(
    name="ChapterBody",
    fontSize=11,
    leading=16,
    spaceAfter=10
))


# ------------------ SCRAPER ------------------

def fetch_chapter(ch_no, max_retries=2):
    url = f"{cfg.BASE_URL}{ch_no}"
    last_exception = None

    for attempt in range(1, max_retries + 2):
        try:
            r = session.get(url, timeout=45)
            r.raise_for_status()

            soup = BeautifulSoup(r.text, "html.parser")

            # ---- TITLE ----
            title_tag = soup.select_one("div.cur a[title^='Chapter']")
            title = title_tag.get_text(strip=True) if title_tag else f"Chapter {ch_no}"

            # ---- CONTENT ----
            content_div = soup.select_one("div.txt")
            if not content_div:
                raise ValueError("Chapter text not found")

            paragraphs = [
                p.get_text(strip=True)
                for p in content_div.find_all("p")
                if p.get_text(strip=True)
            ]

            if not paragraphs:
                raise ValueError("Empty chapter")

            return title, paragraphs

        except (requests.exceptions.RequestException, ValueError) as e:
            last_exception = e
            if attempt <= max_retries:
                wait = 2 * attempt
                logger.warning(
                    f"[JOB {job_id}] Chapter {ch_no} failed "
                    f"(attempt {attempt}), retrying in {wait}s"
                )
                time.sleep(wait)
            else:
                logger.error(
                    f"[JOB {job_id}] Chapter {ch_no} failed permanently"
                )

    raise last_exception


# ------------------ PDF BUILDER ------------------

def build_pdf(chapters, start, end):
    filename = f"{chat_id}__{safe_title}_{start}_to_{end}.pdf"
    path = os.path.join(cfg.OUTPUT_DIR, filename)
    backupPath = os.path.join("backups", filename)

    logger.info(f"[JOB {job_id}] Writing PDF: {filename}")

    doc = SimpleDocTemplate(
        path,
        pagesize=A4,
        rightMargin=1 * inch,
        leftMargin=1 * inch,
        topMargin=1 * inch,
        bottomMargin=1 * inch
    )
    
    backupdoc = SimpleDocTemplate(
        backupPath,
        pagesize=A4,
        rightMargin=1 * inch,
        leftMargin=1 * inch,
        topMargin=1 * inch,
        bottomMargin=1 * inch
    )

    story = []

    for title, paras in chapters:
        story.append(Paragraph(title, styles["ChapterTitle"]))
        story.append(Spacer(1, 0.2 * inch))

        for p in paras:
            story.append(Paragraph(p, styles["ChapterBody"]))

        story.append(PageBreak())

    doc.build(story)
    backupdoc.build(story)

    logger.info(f"[JOB {job_id}] PDF written successfully: {filename}")
    return path,backupPath


# ------------------ MAIN ------------------

buffer = []
job_status = "running"
error_message = None

try:
    for ch in range(cfg.START_CHAPTER, cfg.END_CHAPTER + 1):
        logger.info(f"[JOB {job_id}] Fetching chapter {ch}")

        buffer.append(fetch_chapter(ch))
        time.sleep(2)

        # progress update
        with open(job_file, "w") as f:
            json.dump({
                "job_id": job_id,
                "chat_id": chat_id,
                "novel": novel_title,
                "start": cfg.START_CHAPTER,
                "end": cfg.END_CHAPTER,
                "current": ch,
                "status": "running"
            }, f)

    # PDF generation
    build_pdf(buffer, cfg.START_CHAPTER, cfg.END_CHAPTER)
    logger.info(f"[JOB {job_id}] PDF generation complete")

    job_status = "completed"

except Exception as e:
    job_status = "failed"
    error_message = str(e)

    logger.exception(f"[JOB {job_id}] Job failed")

finally:
    # 🔥 FINAL, HONEST STATE
    with open(job_file, "w") as f:
        payload = {
            "job_id": job_id,
            "chat_id": chat_id,
            "novel": novel_title,
            "start": cfg.START_CHAPTER,
            "end": cfg.END_CHAPTER,
            "current": (
                cfg.END_CHAPTER if job_status == "completed" else ch
            ),
            "status": job_status
        }

        if error_message:
            payload["error"] = error_message

        json.dump(payload, f)

    logger.info(
        f"[JOB {job_id}] Job finished with status = {job_status}"
    )
