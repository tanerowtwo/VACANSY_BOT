import os
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from aiohttp import web

# === ENV ===
api_id = int(os.environ["API_ID"])
api_hash = os.environ["API_HASH"]
string_session = os.environ["STRING_SESSION"]
FRIEND_ID = int(os.environ.get("FRIEND_ID", "0"))

# === HTTP сервер ===
async def handle(request):
    return web.Response(text="OK", content_type="text/plain")

async def web_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(
        runner,
        "0.0.0.0",
        int(os.environ.get("PORT", 8080))
    )
    await site.start()
    print("🌐 Web server started")

# === TELEGRAM ЛОГИКА ===
async def start_telegram():
    while True:  # автоперезапуск если упадёт
        try:
            print("🚀 Starting client...")

            client = TelegramClient(
                StringSession(string_session),
                api_id,
                api_hash
            )

            @client.on(events.NewMessage)
            async def handler(event):
                try:
                    if not event.is_private:
                        return

                    sender = await event.get_sender()

                    if sender.id != FRIEND_ID:
                        return

                    text = (event.message.message or "").lower()

                    if "instagram.com" in text or "instagr.am" in text:
                        await asyncio.sleep(0.3)
                        await event.delete()
                        print("❌ Удалено сообщение с Instagram")

                except Exception as e:
                    print(f"⚠️ Handler error: {e}")

            await client.start()
            print("🤖 Бот запущен")

            await client.run_until_disconnected()

        except Exception as e:
            print(f"💥 Telegram crashed: {e}")
            print("🔄 Перезапуск через 5 секунд...")
            await asyncio.sleep(5)

# === MAIN ===
async def main():
    print("🟡 Starting services...")

    # сначала веб-сервер
    await web_server()

    # потом телеграм в фоне
    asyncio.create_task(start_telegram())

    # держим процесс живым
    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())
