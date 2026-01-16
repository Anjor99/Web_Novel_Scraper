import requests
from bs4 import BeautifulSoup

BASE_SITE = "https://freewebnovel.com"

CUSTOM_NOVELS = {
    "My Werewolf System": {
        "slug": "https://freewebnovel.com/novel/my-werewolf-system-novel/chapter-",
        "total_chapters": None
    }
}

def fetch_top_5_popular():
    r = requests.get(f"{BASE_SITE}/sort/most-popular", timeout=30)
    soup = BeautifulSoup(r.text, "html.parser")

    novels = []
    for row in soup.select("div.li-row")[:5]:
        title = row.select_one("h3.tit a").text.strip()
        slug = row.select_one("h3.tit a")["href"]
        chapters = int(row.select_one("span.s1").text.split()[0])

        novels.append({
            "title": title,
            "slug": f"{BASE_SITE}{slug}/chapter-",
            "total_chapters": chapters
        })
    return novels

def get_all_novels():
    novels = fetch_top_5_popular()
    for title, data in CUSTOM_NOVELS.items():
        novels.append({
            "title": title,
            "slug": data["slug"],
            "total_chapters": data["total_chapters"]
        })
    return novels
