import os
import time
import requests
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from config import Config

# ------------------ CONFIG ------------------
cfg = Config()

os.makedirs(cfg.OUTPUT_DIR, exist_ok=True)

# ------------------ SESSION ------------------

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

    for attempt in range(1, max_retries + 4):  # first try + retries
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

            return title, paragraphs  # ✅ success

        except (requests.exceptions.RequestException, ValueError) as e:
            last_exception = e
            if attempt <= max_retries:
                wait_time = 2 * attempt
                print(f"⚠️ Chapter {ch_no} failed (attempt {attempt}), retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"❌ Chapter {ch_no} failed after {max_retries + 1} attempts")

    raise last_exception

# ------------------ PDF BUILDER ------------------

def build_pdf(chapters, start, end):
    output_file = f"{cfg.OUTPUT_DIR}/MWS_{start}_to_{end}.pdf"

    doc = SimpleDocTemplate(
        output_file,
        pagesize=A4,
        rightMargin=1*inch,
        leftMargin=1*inch,
        topMargin=1*inch,
        bottomMargin=1*inch
    )

    story = []

    for title, paras in chapters:
        story.append(Paragraph(title, styles["ChapterTitle"]))
        story.append(Spacer(1, 0.2 * inch))
        for p in paras:
            story.append(Paragraph(p, styles["ChapterBody"]))
        story.append(PageBreak())

    doc.build(story)
    print(f"✅ Created {output_file}")
