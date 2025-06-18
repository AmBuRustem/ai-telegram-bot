
import feedparser
import time
import requests
import re
import os
import subprocess
from bs4 import BeautifulSoup

BOT_TOKEN = "7992455449:AAFO-JyPCJ48tsAUwYyfZzhhW5hOnF-XyVw"
CHAT_ID = "@shtormnews"

# 🔹 Расширенные RSS-источники с высоким шансом видео
RSS_FEEDS = [
    'https://www.ntv.ru/exp/news.rss',
    'https://www.1tv.ru/export/news.xml',
    'https://russian.rt.com/rss',
    'https://360tv.ru/rss/',
    'https://www.vesti.ru/vesti.rss',
    'https://iz.ru/xml/rss/all.xml',
    'https://ria.ru/export/rss2/archive/index.xml'
]

VIRAL_KEYWORDS = [
    "пожар", "взорвал", "арест", "задержан", "дтп", "авария",
    "теракт", "взрыв", "огонь", "убийство", "Telegram",
    "звезда", "блогер", "чп", "скандал", "катастрофа", "полиция"
]

posted_links = set()

headers = {
    "User-Agent": "Mozilla/5.0 (compatible; ShtormBot/1.0)"
}

def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    return re.sub(cleanr, '', raw_html).strip()

def build_caption(title, description):
    title = f"<b>⚡ {title.strip()}</b>"
    desc = clean_html(description)
    if len(desc) > 300:
        desc = desc[:297] + "..."
    return f"{title}\n\n{desc}\n\n📡 @shtormnews"

def is_viral(title, description):
    text = (title + " " + description).lower()
    return any(kw in text for kw in VIRAL_KEYWORDS)

def download_video(entry_url, filename="video.mp4"):
    try:
        subprocess.run(
            ["yt-dlp", "-f", "mp4", "-o", filename, entry_url],
            check=True
        )
        return os.path.exists(filename)
    except Exception as e:
        print("Ошибка загрузки видео:", e)
        return False

def send_video_file(filename, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo"
    with open(filename, 'rb') as video:
        files = {'video': video}
        data = {'chat_id': CHAT_ID, 'caption': caption, 'parse_mode': 'HTML'}
        r = requests.post(url, data=data, files=files)
        if r.status_code == 429:
            wait = int(re.findall(r'retry after (\d+)', r.text)[0])
            print(f"⏳ Задержка Telegram: {wait} сек.")
            time.sleep(wait)
        elif r.status_code != 200:
            print("Ошибка отправки видео:", r.text)
        else:
            time.sleep(10)

def send_text(caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {'chat_id': CHAT_ID, 'text': caption, 'parse_mode': 'HTML'}
    r = requests.post(url, data=data)
    if r.status_code == 429:
        wait = int(re.findall(r'retry after (\d+)', r.text)[0])
        print(f"⏳ Задержка Telegram: {wait} сек.")
        time.sleep(wait)
    elif r.status_code != 200:
        print("Ошибка отправки текста:", r.text)
    else:
        time.sleep(10)

def get_news():
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        count = 0
        for entry in feed.entries:
            if count >= 2:
                break
            if entry.link in posted_links:
                continue
            title = entry.title
            description = entry.get("description", "")
            if not is_viral(title, description):
                continue
            posted_links.add(entry.link)
            count += 1
            caption = build_caption(title, description)

            if download_video(entry.link):
                send_video_file("video.mp4", caption)
                os.remove("video.mp4")
            else:
                send_text(caption)

if __name__ == "__main__":
    while True:
        try:
            get_news()
            time.sleep(300)
        except Exception as e:
            print("Ошибка в основном цикле:", e)
            time.sleep(60)
