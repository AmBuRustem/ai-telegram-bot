
import feedparser
import time
import requests
import re
import json

BOT_TOKEN = "7992455449:AAFO-JyPCJ48tsAUwYyfZzhhW5hOnF-XyVw"
CHAT_ID = "@shtormnews"

RSS_FEEDS = [
    'https://lenta.ru/rss/news',
    'https://life.ru/rss',
    'https://www.mk.ru/rss/news/index.xml',
    'https://www.starhit.ru/rss.xml',
]

posted_links = set()

def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    return re.sub(cleanr, '', raw_html).strip()

def send_request(url, data, method="text", media_url=None):
    for attempt in range(3):
        try:
            if method == "video":
                data["video"] = media_url
                response = requests.post(url, data=data)
            elif method == "photo":
                data["photo"] = media_url
                response = requests.post(url, data=data)
            else:
                response = requests.post(url, data=data)

            if response.status_code == 429:
                wait_time = json.loads(response.text).get("parameters", {}).get("retry_after", 30)
                print(f"Too many requests — пауза {wait_time} сек")
                time.sleep(wait_time + 1)
            elif response.status_code != 200:
                print(f"Ошибка отправки ({method}):", response.text)
                return False
            else:
                time.sleep(1)  # Защита от частых отправок
                return True
        except Exception as e:
            print(f"Ошибка при попытке {attempt+1}: {e}")
            time.sleep(2)
    return False

def send_video(video_url, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo"
    data = {'chat_id': CHAT_ID, 'caption': caption, 'parse_mode': 'HTML'}
    return send_request(url, data, method="video", media_url=video_url)

def send_photo(photo_url, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    data = {'chat_id': CHAT_ID, 'caption': caption, 'parse_mode': 'HTML'}
    return send_request(url, data, method="photo", media_url=photo_url)

def send_text(caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {'chat_id': CHAT_ID, 'text': caption, 'parse_mode': 'HTML'}
    return send_request(url, data, method="text")

def get_media(entry):
    media_url = None
    if 'media_content' in entry:
        for media in entry.media_content:
            if 'video' in media.get('type', ''):
                return 'video', media['url']
            elif 'image' in media.get('type', ''):
                media_url = media['url']
    if 'links' in entry:
        for link in entry.links:
            if link.get('type', '').startswith('video'):
                return 'video', link['href']
            elif link.get('type', '').startswith('image'):
                media_url = link['href']
    if 'image' in entry:
        return 'photo', entry.image
    if media_url:
        return 'photo', media_url
    return None, None

def build_caption(title, description):
    title = f"<b>⚡ {title.strip()}</b>"
    desc = clean_html(description)
    if len(desc) > 300:
        desc = desc[:297] + "..."
    return f"{title}\n\n{desc}\n\n📡 @shtormnews"

def get_news():
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            if entry.link in posted_links:
                continue
            posted_links.add(entry.link)
            title = entry.title
            description = entry.get("description", "")
            caption = build_caption(title, description)
            media_type, media_url = get_media(entry)
            success = False
            if media_type == "video":
                success = send_video(media_url, caption)
            elif media_type == "photo":
                success = send_photo(media_url, caption)
            if not success:
                send_text(caption)

if __name__ == "__main__":
    while True:
        try:
            get_news()
            time.sleep(300)
        except Exception as e:
            print("Ошибка:", e)
            time.sleep(60)
