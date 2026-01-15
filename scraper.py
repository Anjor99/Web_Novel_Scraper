import requests
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

BASE_URL = "https://www.empirenovel.com/novel/my-werewolf-system/"
START_CHAPTER = 1
END_CHAPTER = 50

OUTPUT_FILE = "My_Werewolf_System_Chapters_1_to_50.pdf"

headers = {
    "User-Agent": "Mozilla/5.0"
}

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name="ChapterTitle",
    fontSize=16,
    spaceAfter=14,
    spaceBefore=20,
    leading=20
))

styles.add(ParagraphStyle(
    name="BodyText",
    fontSize=11,
    leading=16,
    spaceAfter=10
))

doc = SimpleDocTemplate(
    OUTPUT_FILE,
    pagesize=A4,
    rightMargin=1*inch,
    leftMargin=1*inch,
    topMargin=1*inch,
    bottomMargin=1*inch
)

story = []

def fetch_chapter(chapter_no):
    url = f"{BASE_URL}{chapter_no}"
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # Chapter title
    title_tag = soup.find("h1")
    title = title_tag.get_text(strip=True) if title_tag else f"Chapter {chapter_no}"

    # Chapter content
    content_div = soup.find("div", class_="chapter-content")
    if not content_div:
        raise ValueError(f"Content not found for chapter {chapter_no}")

    paragraphs = [p.get_text(strip=True) for p in content_div.find_all("p") if p.get_text(strip=True)]
    return title, paragraphs


for chapter in range(START_CHAPTER, END_CHAPTER + 1):
    print(f"Fetching chapter {chapter}...")
    try:
        title, paragraphs = fetch_chapter(chapter)

        story.append(Paragraph(title, styles["ChapterTitle"]))
        Spacer(1, 0.2 * inch)

        for para in paragraphs:
            story.append(Paragraph(para, styles["BodyText"]))

        story.append(PageBreak())

    except Exception as e:
        print(f"❌ Failed chapter {chapter}: {e}")

doc.build(story)
print(f"\n✅ PDF created: {OUTPUT_FILE}")
