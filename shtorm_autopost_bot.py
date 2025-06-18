
import feedparser
import time
import requests

BOT_TOKEN = '7992455449:AAFO-JyPCJ48tsAUwYyfZzhhW5hOnF-XyVw'
CHAT_ID = '@shtormnews'

RSS_FEEDS = [
    'https://lenta.ru/rss/news',
    'https://life.ru/rss',
    'https://www.mk.ru/rss/news/index.xml',
    'https://www.starhit.ru/rss.xml',
]

posted_links = set()

def get_news():
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            if entry.link not in posted_links:
                title = entry.title
                link = entry.link
                message = "⚡ <b>{}</b>\n{}\n\n#новости #шок #шторм".format(title, link)
                send_message(message)
                posted_links.add(entry.link)

def send_message(text):
    url = "https://api.telegram.org/bot{}/sendMessage".format(BOT_TOKEN)
    data = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    response = requests.post(url, data=data)
    if response.status_code != 200:
        print("Ошибка отправки:", response.text)

if __name__ == "__main__":
    while True:
        try:
            get_news()
            time.sleep(300)
        except Exception as e:
            print("Ошибка:", e)
            time.sleep(60)
