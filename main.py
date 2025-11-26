import os
import asyncio
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
    "я сведу ваши лучшие кадры", "хочешь такой же монтаж",
    "свободен для проектов", "свободен для новых проектов", "летаю на дронах",
    "я начинающий монтажер", "я fulltime колорист", "я являюсь видеомонтажером",
    "я знаю толк в монтаже", "ваше сообщение удалено", "улетит в @ru_montage_pins",
    "ищу смм-менеджера.", "делаю волшебство в сфере монтажа", "clarity design",
    "@winerooo", "@kartinsky", "смонтирую бесплатно парочку",
    "https://t.me/andrews_hurricane", "превращу ваши исходники",
    "пишите — обсудим ваш проект!", "@lykiardtg", "emalzp",
    "монтаж который приносит людям результаты", "@frutell04ka", "мои работы",
    "у тебя нет времени на монтаж", "@the13tn", "@anwazzup",
    "я занимаюсь видеомонтажом.", "@karinakraskj", "ищу заказы",
    "я олег — видеомонтажер", "@ragestrike", "@minec0mmand",
    "https://t.me/prtflconsence", "@terpkiy56", "https://t.me/eprikyanedit",
    "@kanexlz", "я дипломированный опытный", "занимаюсь созданием роликов",
    "смонтирую любой ваш контент", "@tamedghost", "@iamyownmuse",
    "я — видеомонтажёр,", "я — видеомонтажёр", "кастинг актеров",
    "предоставляю услуги", "работаю в видеомонтаже", "@abramov_prod",
    "почему твои видео не работают.", "предлагаю свои услуги", "@moshpitedit",
    "буду рад выйти на ваш проект", "@simon_rotkiv",
    "я специализируюсь на монтаже видео.", "я специализируюсь на монтаже видео",
    "я fulltime колорист", "монтаж для потребителя", "@daniilvfx", "@cgtesto",
    "свободен, ищу проекты", "монтирую круто", "я видео монтажёр",
    "@zinckprod", "ищу работу", "ищу начинающего", "@osukhovskiyfilms",
    "@sabo_tg",
    "нужен качественный монтаж?", "буду рада выйти", "готова выйти",
    "@film_post_production", "стану вашим монтажером", "@leifu",
    "@tati_lead_manager", "@kugukanton", "@emifilm",
    "монтаж который даст тебе результаты", "@tsujiss",
    "@aladdin_videomaker", "могу выйти на ваш проект",
    "я специализируюсь на монтаже",
    "я — профессиональный монтажёр", "традиционная акция уже близко!",
    "1 - h.264/265", "@vladin98", "ищу смм", "список основных триггеров:",
    "я профессиональный колорист", "ищите ответственного монтажёра?",
    "@asens410", "ищу девушку монтажерку для отношений",
    "делаю бесплатный монтаж", "https://t.me/jump_cut/773",
    "ищу проекты в портфолио", "бесплатный монтаж видео",
    "https://t.me/portgromov", "@smaryd1", "telegram:@smaryd1",
    "готов бесплатно смонтировать", "я режиссер монтажа",
    "открыт к проектам", "@pslnnn", "@radicalsubject", "@logovosrg",
    "я профессиональный колорист", "работаю в davinci resolve",
    "ищите ответственного монтажёра?", "я видеограф"
]


client = TelegramClient(StringSession(string_session), api_id, api_hash)

# === Фильтр сообщений ===
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


# === HTTP сервер Render ===
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


# === Keep-Alive для Render ===
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
    print("🤖 Бот запущен и слушает чаты...")

    asyncio.create_task(web_server())
    asyncio.create_task(heartbeat())
    asyncio.create_task(keep_alive())

    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())



