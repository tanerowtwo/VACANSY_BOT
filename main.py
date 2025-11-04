import os
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from aiohttp import web

# === Настройки аккаунта ===
api_id = int(os.environ.get("API_ID", "23246373"))  # твой API ID
api_hash = os.environ.get("API_HASH", "daa39e9d5b1bc1261b0c3e27853205fc")  # твой API HASH
string_session = os.environ.get("STRING_SESSION")  # вставь STRING_SESSION в переменные окружения
target_chat = int(os.environ.get("TARGET_CHAT", "-4734945370"))  # ID или username чата для пересылки

# === Слова для фильтрации ===
include_words = [
    "монтаж", "монтажер", "#ищу_монтаж", "монтажера",
    "екатеринбург", "екб", "колорист", "покрасить", "магнитогорск"
]

exclude_words = [
    "#ищу_работу", "#ищуработу"
]

# === Создаём Telethon клиента ===
client = TelegramClient(StringSession(string_session), api_id, api_hash)

# === Обработчик сообщений ===
@client.on(events.NewMessage)
async def handler(event):
    try:
        if not event.message.message:
            return

        message_text = event.message.message.lower()

        # Проверка фильтров
        if any(word in message_text for word in include_words) and not any(bad in message_text for bad in exclude_words):
            chat = await event.get_chat()
            sender = await event.get_sender()

            # Название чата
            chat_name = getattr(chat, "title", None) or getattr(chat, "username", None) or "Неизвестный чат"

            # Имя отправителя
            sender_name = getattr(sender, "first_name", None) or getattr(sender, "title", None) or "Неизвестно"

            text = (
                f"📢 Из чата: {chat_name}\n"
                f"👤 От: {sender_name}\n\n"
                f"{event.message.message}"
            )

            await client.send_message(target_chat, text)
            print(f"✅ Переслано сообщение из {chat_name}")
    except Exception as e:
        print(f"⚠️ Ошибка: {e}")

# === aiohttp сервер для Render (держит процесс активным) ===
async def handle(request):
    return web.Response(text="✅ Bot is running")

async def web_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.environ.get("PORT", 8080)))
    await site.start()
    print(f"🌐 Web server listening on port {os.environ.get('PORT', 8080)}")

# === Основной запуск ===
async def main():
    await client.start()
    print("🤖 Бот запущен и слушает чаты...")

    # Запуск обоих процессов параллельно
    await asyncio.gather(
        client.run_until_disconnected(),
        web_server()
    )

if __name__ == "__main__":
    asyncio.run(main())
