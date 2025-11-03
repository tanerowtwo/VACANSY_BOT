import os
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# ================== Настройки ==================
api_id = int(os.environ.get("API_ID"))
api_hash = os.environ.get("API_HASH")
string_session = os.environ.get("STRING_SESSION")
target_chat_env = os.environ.get("TARGET_CHAT", "me")

# Если передан числовой ID — приводим к int, иначе оставляем строку (например "@username")
try:
    target_chat = int(target_chat_env)
except Exception:
    target_chat = target_chat_env

# Слова для фильтрации
include_words = [
    "монтаж", "монтажер", "#ищу_монтаж", "монтажера",
    "екатеринбург", "екб", "колорист", "покрасить", "магнитогорск"
]
exclude_words = [
    "#ищу_работу", "#ищуработу"
]

# ================== Telethon client ==================
client = TelegramClient(StringSession(string_session), api_id, api_hash)

@client.on(events.NewMessage)
async def handler(event):
    try:
        # безопасно получаем текст (могут быть сообщения без .message)
        message_text = (event.message.message or "").lower()

        if any(word in message_text for word in include_words) and not any(bad in message_text for bad in exclude_words):
            chat = await event.get_chat()
            sender = await event.get_sender()

            # корректное имя чата
            if hasattr(chat, 'title'):
                chat_name = chat.title
            elif hasattr(chat, 'username'):
                chat_name = chat.username
            else:
                chat_name = getattr(chat, 'first_name', 'Неизвестный чат')

            # корректное имя отправителя
            if hasattr(sender, 'first_name'):
                sender_name = sender.first_name
            elif hasattr(sender, 'username'):
                sender_name = sender.username
            else:
                sender_name = str(sender)

            text = (
                f"📢 Из чата: {chat_name}\n"
                f"👤 От: {sender_name}\n\n"
                f"{event.message.message}"
            )

            await client.send_message(target_chat, text)

    except Exception as e:
        # печатаем ошибку в лог, но не падаем
        print("⚠️ Ошибка при обработке сообщения:", repr(e))

# ================== Запуск Telethon и HTTP health ==================
async def start_telethon():
    # Запускаем клиент и ждём отключения (работает постоянно)
    await client.start()
    print("✅ Telethon client started")
    await client.run_until_disconnected()

async def start_health_server():
    # Простой HTTP endpoint, чтобы Render видел, что сервис жив
    from aiohttp import web

    async def handle(request):
        return web.Response(text="OK")

    app = web.Application()
    app.router.add_get("/", handle)

    port = int(os.environ.get("PORT", "8000"))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"✅ Health server listening on 0.0.0.0:{port}")

    # держим задачу живой
    while True:
        await asyncio.sleep(3600)

async def main():
    # запускаем параллельно Telethon и health server
    await asyncio.gather(
        start_telethon(),
        start_health_server()
    )

if __name__ == "__main__":
    # запускаем главный цикл
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopping...")
