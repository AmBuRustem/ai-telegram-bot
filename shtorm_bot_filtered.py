
import feedparser
import time
import requests
import re
from bs4 import BeautifulSoup

BOT_TOKEN = "7992455449:AAFO-JyPCJ48tsAUwYyfZzhhW5hOnF-XyVw"
CHAT_ID = "@shtormnews"

RSS_FEEDS = [
    'https://lenta.ru/rss/news',
    'https://life.ru/rss',
    'https://www.mk.ru/rss/news/index.xml',
    'https://www.starhit.ru/rss.xml',
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

def extract_video_from_page(url):
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            return None
        soup = BeautifulSoup(resp.text, 'html.parser')
        video = soup.find('video')
        if video and video.get('src'):
            return video['src']
        iframe = soup.find('iframe')
        if iframe and 'video' in iframe.get('src', ''):
            return iframe['src']
    except Exception as e:
        print("Ошибка при загрузке страницы:", e)
    return None

def send_video(video_url, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo"
    data = {'chat_id': CHAT_ID, 'video': video_url, 'caption': caption, 'parse_mode': 'HTML'}
    r = requests.post(url, data=data)
    handle_response(r, "видео")

def send_photo(photo_url, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    data = {'chat_id': CHAT_ID, 'photo': photo_url, 'caption': caption, 'parse_mode': 'HTML'}
    r = requests.post(url, data=data)
    handle_response(r, "фото")

def send_text(caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {'chat_id': CHAT_ID, 'text': caption, 'parse_mode': 'HTML'}
    r = requests.post(url, data=data)
    handle_response(r, "текст")

def handle_response(r, content_type):
    if r.status_code == 429:
        wait = int(re.findall(r'retry after (\d+)', r.text)[0])
        print(f"⏳ Задержка Telegram: {wait} сек.")
        time.sleep(wait)
    elif r.status_code != 200:
        print(f"Ошибка отправки {content_type}:", r.text)
    else:
        time.sleep(10)  # интервал между постами

def build_caption(title, description):
    title = f"<b>⚡ {title.strip()}</b>"
    desc = clean_html(description)
    if len(desc) > 300:
        desc = desc[:297] + "..."
    return f"{title}\n\n{desc}\n\n📡 @shtormnews"

def is_viral(title, description):
    text = (title + " " + description).lower()
    return any(kw in text for kw in VIRAL_KEYWORDS)

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

            video_url = extract_video_from_page(entry.link)
            if video_url and video_url.endswith(('.mp4', '.webm')):
                send_video(video_url, caption)
                continue

            image_url = None
            if 'media_content' in entry:
                for m in entry.media_content:
                    if 'image' in m.get('type', ''):
                        image_url = m['url']
            elif 'links' in entry:
                for link in entry.links:
                    if link.get('type', '').startswith('image'):
                        image_url = link['href']

            if image_url:
                send_photo(image_url, caption)
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
