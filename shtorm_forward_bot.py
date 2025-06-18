
from telethon import TelegramClient, events
import asyncio
import re
import random

# ✅ Telegram API данные
api_id = 26232340
api_hash = '6bb113f9e12926d4dc1f56a89ab6534f'
session_name = 'shtorm_session'

# ✅ Канал-приёмник
TARGET_CHANNEL = 'shtormnews'

# ✅ Каналы-источники
SOURCE_CHANNELS = [
    'bazabazon',
    'shot_shot',
    'readovkanews',
    'ENews112',
    'bezzludey'
]

# 🔁 Уникализация текста
def rewrite_text(text):
    if not text:
        return ""
    replacements = {
        "произошло": "случилось",
        "сообщают": "передают",
        "появилось видео": "опубликованы кадры",
        "видео": "видеозапись",
        "кадры": "запись",
        "инцидент": "событие",
        "на месте": "по данным с места",
        "в сети": "в интернете"
    }
    for old, new in replacements.items():
        text = re.sub(rf'\b{old}\b', new, text, flags=re.IGNORECASE)
    return text.strip()

# ✅ Формируем подпись
def build_caption(original_text, sender):
    unique = rewrite_text(original_text)
    footer = f"\n\n<i>Источник медиа: @{sender}</i>"
    return unique + footer if unique else footer

client = TelegramClient(session_name, api_id, api_hash)

@client.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def handler(event):
    sender = (await event.get_chat()).username
    if not sender:
        return

    # Только если есть медиа
    if event.photo or event.video or event.document:
        original_text = event.message.text or ""
        caption = build_caption(original_text, sender)
        try:
            await client.send_message(
                entity=TARGET_CHANNEL,
                file=event.media,
                message=caption,
                parse_mode='html'
            )
            print(f"✅ Пост опубликован из @{sender}")
        except Exception as e:
            print(f"Ошибка отправки: {e}")

async def main():
    print("🤖 Бот слушает источники...")
    await client.start()
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
