
import feedparser
import time
import requests
from html import unescape
from bs4 import BeautifulSoup

BOT_TOKEN = "7992455449:AAFO-JyPCJ48tsAUwYyfZzhhW5hOnF-XyVw"
CHAT_ID = "@shtormnews"

RSS_FEEDS = [
    'https://lenta.ru/rss/news',
    'https://life.ru/rss',
    'https://www.mk.ru/rss/news/index.xml',
    'https://www.starhit.ru/rss.xml',
]

posted_links = set()

def clean_description(raw_html):
    if not raw_html:
        return ""
    soup = BeautifulSoup(unescape(raw_html), "html.parser")
    text = soup.get_text().strip()
    return text[:300] + "..." if len(text) > 300 else text

def send_video(video_url, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo"
    data = {
        'chat_id': CHAT_ID,
        'video': video_url,
        'caption': caption,
        'parse_mode': 'HTML'
    }
    response = requests.post(url, data=data)
    if response.status_code != 200:
        print("Ошибка отправки видео:", response.text)

def send_photo(photo_url, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    data = {
        'chat_id': CHAT_ID,
        'photo': photo_url,
        'caption': caption,
        'parse_mode': 'HTML'
    }
    response = requests.post(url, data=data)
    if response.status_code != 200:
        print("Ошибка отправки фото:", response.text)

def send_text(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        'chat_id': CHAT_ID,
        'text': text,
        'parse_mode': 'HTML'
    }
    response = requests.post(url, data=data)
    if response.status_code != 200:
        print("Ошибка отправки текста:", response.text)

def get_news():
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            if entry.link not in posted_links:
                title = entry.title
                link = entry.link
                desc = clean_description(entry.get("description", ""))
                media_url = ""

                # Поиск видео или изображения
                if "media_content" in entry:
                    for media in entry.media_content:
                        if "video" in media.get("type", ""):
                            media_url = media["url"]
                            send_video(media_url, f"<b>⚡ {title}</b>\n\n{desc}\n\n📡 @shtormnews")
                            break
                        elif "image" in media.get("type", "") and not media_url:
                            media_url = media["url"]
                elif "links" in entry:
                    for link_data in entry.links:
                        if link_data.get("type", "").startswith("video"):
                            media_url = link_data["href"]
                            send_video(media_url, f"<b>⚡ {title}</b>\n\n{desc}\n\n📡 @shtormnews")
                            break
                        elif link_data.get("type", "").startswith("image") and not media_url:
                            media_url = link_data["href"]

                if media_url and not media_url.endswith(".mp4"):
                    send_photo(media_url, f"<b>⚡ {title}</b>\n\n{desc}\n\n📡 @shtormnews")
                elif not media_url:
                    send_text(f"<b>⚡ {title}</b>\n\n{desc}\n\n📡 @shtormnews")

                posted_links.add(entry.link)

if __name__ == "__main__":
    while True:
        try:
            get_news()
            time.sleep(300)
        except Exception as e:
            print("Ошибка:", e)
            time.sleep(60)
