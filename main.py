import os
import asyncio
import urllib.parse
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from aiohttp import web

api_id = int(os.environ["API_ID"])
api_hash = os.environ["API_HASH"]
string_session = os.environ["STRING_SESSION"]
target_chat = int(os.environ.get("TARGET_CHAT", "-4734945370"))

include_words = [
    "монтаж", "монтажер", "#ищу_монтаж", "монтажера", "смонтировать",
    "екатеринбург", "екб", "колорист", "покрасить", "цветокоррекция", "магнитогорск", "челябинск"
]

exclude_words = [ ... ]  # оставь свой список как есть

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

            username = getattr(sender, "username", None)
            user_id = sender.id

            # Кликабельный отправитель
            if username:
                sender_display = f'<a href="https://t.me/{username}">@{username}</a>'
            else:
                sender_display = f'<a href="tg://user?id={user_id}">Пользователь</a>'

            # === Шаблоны откликов ===
            msg1 = (
                "Здравствуйте! Пишу по поводу монтажа.\n\nМои работы: https://disk.yandex.ru/d/CCI5jUdmZfH1gg"
            )

            msg2 = (
                "Добрый день! Пишу по поводу монтажа.\n\nМои работы: https://disk.yandex.ru/d/CCI5jUdmZfH1gg"
            )

            msg3 = (
                "Приветствую! Пишу по поводу монтажа.\n\nМои работы: https://disk.yandex.ru/d/CCI5jUdmZfH1gg"
            )

            # Кодируем
            msg1_enc = urllib.parse.quote(msg1)
            msg2_enc = urllib.parse.quote(msg2)
            msg3_enc = urllib.parse.quote(msg3)

            # === Ссылки вместо кнопок ===
            links = ""
            if username:
                links = (
                    f"\n\n💬 Отклики:\n"
                    f"— <a href='https://t.me/{username}?text={msg1_enc}'>Здр</a>\n"
                    f"— <a href='https://t.me/{username}?text={msg2_enc}'>Дбд</a>\n"
                    f"— <a href='https://t.me/{username}?text={msg3_enc}'>Прив</a>\n"
                )

            text = (
                f"📢 Из чата: {chat_name}\n"
                f"👤 От: {sender_display}\n\n"
                f"{event.message.message}"
                f"{links}"
            )

            await client.send_message(target_chat, text, parse_mode="html")

            print(f"✅ Переслано сообщение из {chat_name}")

    except Exception as e:
        print(f"⚠️ Ошибка: {e}")


# === HTTP сервер ===
async def handle(request):
    return web.Response(text="OK", content_type="text/plain")

async def web_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.environ.get("PORT", 8080)))
    await site.start()
    print("🌐 Web server started")


# === Heartbeat ===
async def heartbeat():
    while True:
        try:
            me = await client.get_me()
            print(f"💓 Heartbeat OK — {me.username}")
        except Exception as e:
            print(f"💔 Heartbeat failed: {e}")
        await asyncio.sleep(120)


# === Keep Alive ===
async def keep_alive():
    import aiohttp
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                await session.get("https://vacansy-bot.onrender.com", timeout=10)
            print("🔄 keep-alive ping ok")
        except Exception as e:
            print(f"❌ keep-alive failed: {e}")
        await asyncio.sleep(120)


# === MAIN ===
async def main():
    await client.start()
    print("🤖 Бот запущен...")

    asyncio.create_task(web_server())
    asyncio.create_task(heartbeat())
    asyncio.create_task(keep_alive())

    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
