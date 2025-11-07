import os
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from aiohttp import web

api_id = int(os.environ.get("API_ID", "23246373"))
api_hash = os.environ.get("API_HASH", "daa39e9d5b1bc1261b0c3e27853205fc")
string_session = os.environ.get("STRING_SESSION")
target_chat = int(os.environ.get("TARGET_CHAT", "-4734945370"))

include_words = [
    "монтаж", "монтажер", "#ищу_монтаж", "монтажера", "смонтировать",
    "екатеринбург", "екб", "колорист", "покрасить", "цветокоррекция", "магнитогорск", "челябинск"
]

exclude_words = [
    "#ищу_работу", "#ищуработу", "я видеомонтажёр", "занимаюсь монтажом", "#резюме", 
    "нахожусь в поисках проектов", "я монтажёр", "я видеомонтажер", "я монтажер", 
    "#портфолио", "#помогу", "#рилсмейкер", "предлагаю свою кандидатуру", 
    "делаю монтаж", "мое портфолио", "я #видеомонтажёр", "работаю с блогерами", 
    "reels / shorts / tiktok", "добро пожаловать в группу шапка чат.", 
    "я занимаюсь монтажом", "создам красивую картинку", "я монтирую", 
    "я помогу тебе", "мой монтаж", "предлагаю услуги", "почему вам стоит выбрать меня", 
    "ищу новые проекты", "я оператор-постановщик", "почему стоит выбрать меня", 
    "reels", "я - монтажер", "занимаюсь монтажом", "я начинающий монтажёр", 
    "я начинающий специалист", "я монтирую", "я видеооператор-монтажер", 
    "я колорист", "я занимаюсь монтажем", "создаю ролики", "мы делаем ролики", 
    "тогда тебе — ко мне", "чем я конкретно занимаюсь", "я оператор-видеомонтажер", 
    "вот что я умею", "я full-time колорист", "сделаю качественный моушен", 
    "я сведу ваши лучшие кадры", "хочешь такой же монтаж"
]

client = TelegramClient(StringSession(string_session), api_id, api_hash)

@client.on(events.NewMessage)
async def handler(event):
    try:
        if not event.message.message:
            return

        msg = event.message.message.lower()
        if any(w in msg for w in include_words) and not any(b in msg for b in exclude_words):
            chat = await event.get_chat()
            sender = await event.get_sender()
            chat_name = getattr(chat, "title", None) or getattr(chat, "username", None) or "Неизвестный чат"
            sender_name = getattr(sender, "first_name", None) or getattr(sender, "title", None) or "Неизвестно"
            text = f"📢 Из чата: {chat_name}\n👤 От: {sender_name}\n\n{event.message.message}"
            await client.send_message(target_chat, text)
            print(f"✅ Переслано сообщение из {chat_name}")
    except Exception as e:
        print(f"⚠️ Ошибка: {e}")

# === HTTP сервер для Render ===
async def handle(request):
    return web.Response(text="✅ Bot is alive")

async def web_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.environ.get("PORT", 8080)))
    await site.start()
    print(f"🌐 Web server listening on port {os.environ.get('PORT', 8080)}")

# === Heartbeat (проверка соединения) ===
async def heartbeat():
    while True:
        try:
            me = await client.get_me()
            print(f"💓 Heartbeat OK — {me.username}")
        except Exception as e:
            print(f"💔 Heartbeat failed: {e}")
        await asyncio.sleep(120)  # каждые 2 минуты

async def main():
    await client.start()
    print("🤖 Бот запущен и слушает чаты...")
    await asyncio.gather(
        client.run_until_disconnected(),
        web_server(),
        heartbeat()
    )

if __name__ == "__main__":
    asyncio.run(main())





