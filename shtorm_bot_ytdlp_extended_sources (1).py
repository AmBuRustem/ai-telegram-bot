
import feedparser
import time
import requests
import re
import os
import subprocess
from bs4 import BeautifulSoup

BOT_TOKEN = "7992455449:AAFO-JyPCJ48tsAUwYyfZzhhW5hOnF-XyVw"
CHAT_ID = "@shtormnews"

# 🔹 Только надёжные источники с работающим видео
RSS_FEEDS = [
    "https://russian.rt.com/rss",
    "https://www.vesti.ru/vesti.rss"
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

def summarize(text):
    clean = clean_html(text)
    sentences = re.split(r'[.!?]', clean)
    return sentences[0].strip() + "." if sentences else clean

def build_caption(title, description):
    title = f"<b>⚡ {title.strip()}</b>"
    summary = summarize(description)
    if len(summary) > 300:
        summary = summary[:297] + "..."
    return f"{title}

{summary}

📡 @shtormnews"

def is_viral(title, description):
    text = (title + " " + description).lower()
    return any(kw in text for kw in VIRAL_KEYWORDS)

def extract_video_url(entry_url):
    try:
        r = requests.get(entry_url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        iframe = soup.find("iframe")
        if iframe and "src" in iframe.attrs:
            return iframe["src"]
    except Exception as e:
        print("Не удалось извлечь iframe:", e)
    return entry_url  # fallback

def download_video(url, filename="video.mp4"):
    try:
        subprocess.run(
            ["yt-dlp", "-f", "mp4", "-o", filename, url],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
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
            print("✅ Видео отправлено")
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

            video_url = extract_video_url(entry.link)
            if download_video(video_url):
                send_video_file("video.mp4", caption)
                os.remove("video.mp4")
            else:
                print(f"⚠️ Видео не удалось скачать: {video_url}")

if __name__ == "__main__":
    while True:
        try:
            get_news()
            time.sleep(300)  # каждые 5 минут
        except Exception as e:
            print("Ошибка в основном цикле:", e)
            time.sleep(60)
