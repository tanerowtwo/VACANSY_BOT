from telethon import TelegramClient, events
from telethon.sessions import StringSession
import os

# === Настройки аккаунта ===
api_id = int(os.environ.get("API_ID", "23246373"))  # твой API ID
api_hash = os.environ.get("API_HASH", "daa39e9d5b1bc1261b0c3e27853205fc")  # твой API HASH
string_session = os.environ.get("STRING_SESSION", "1ApWapzMBuxydJY6mAeYFNDDk4zccOe_hjpmOiJGgrizaNUCgq_YDib8a8Fa_joiTG6QppsZCwiQ-K_fUtMm7yvVbgVEPAVFRT1m8o3C7iRESreJRzBHaxpNnpVN5L0AX8IR1TyeBKu6kmzZx6xIkpRj9BJVq9Sx9-m8oiRlp703Qq3lgWqMoMI1Kc90ysvz0nDh6-b072hULP0kaEHqPKaneiugKeZveI9_lgTUSuYRgVqfhn30txU0L3i1HRQzLcVrxtSwDwp2jdecjxD8TmUMRbdnvGTz3Uzw6QuDKYQWAp0L5c7u-dMLk-DF0xYWSeOQbRhUrwktRXlyEtwP_qctTp1ozKbc=")

# === Слова для фильтрации ===
include_words = [
    "монтаж", "монтажер", "#ищу_монтаж", "монтажера",
    "екатеринбург", "екб", "колорист", "покрасить", "магнитогорск"
]

exclude_words = [
    "#ищу_работу", "#ищуработу"
]

# === Куда пересылать сообщения ===
target_chat = int(os.environ.get("TARGET_CHAT", "-4734945370"))

# === Создаём клиент Telethon ===
client = TelegramClient(StringSession(string_session), api_id, api_hash)

# === Обработчик новых сообщений ===
@client.on(events.NewMessage)
async def handler(event):
    try:
        message_text = event.message.message.lower()

        # Проверка на нужные слова
        if any(word in message_text for word in include_words):
            if not any(bad in message_text for bad in exclude_words):

                chat = await event.get_chat()
                sender = await event.get_sender()

                # --- Определяем корректное имя чата ---
                if hasattr(chat, 'title'):          # Чат или канал
                    chat_name = chat.title
                elif hasattr(chat, 'username'):     # Пользователь с username
                    chat_name = chat.username
                else:                               # Обычный пользователь
                    chat_name = getattr(chat, 'first_name', 'Неизвестный чат')

                # --- Определяем корректное имя отправителя ---
                if hasattr(sender, 'first_name'):
                    sender_name = sender.first_name
                elif hasattr(sender, 'username'):
                    sender_name = sender.username
                else:
                    sender_name = str(sender)  # на всякий случай

                # --- Формируем текст сообщения ---
                text = (
                    f"📢 Из чата: {chat_name}\n"
                    f"👤 От: {sender_name}\n\n"
                    f"{event.message.message}"
                )

                # --- Пересылаем сообщение ---
                await client.send_message(target_chat, text)

    except Exception as e:
        print(f"⚠️ Ошибка: {e}")

# === Запуск бота ===
print("✅ Бот запущен. Слушает чаты...")
client.start()
client.run_until_disconnected()
