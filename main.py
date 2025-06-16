import logging
import uuid
import json
import os

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

API_TOKEN = '8009684168:AAFGQNKsK8EW9wKgoPUlQDZPcJqnZ5BTAC4'
CHANNEL_ID = '@externalzxc'
CHANNEL_LINK = 'https://t.me/externalzxc'
OWNER_ID = 6486157450

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

FILES_PATH = "files.json"
files = {}
visited_users = set()

def load_files():
    global files
    if os.path.exists(FILES_PATH):
        with open(FILES_PATH, 'r', encoding='utf-8') as f:
            files = json.load(f)

def save_files():
    with open(FILES_PATH, 'w', encoding='utf-8') as f:
        json.dump(files, f, indent=4)

async def check_subscription(user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        logging.warning(f'Ошибка проверки подписки: {e}')
        return False

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    args = message.get_args()
    is_new = user_id not in visited_users
    visited_users.add(user_id)

    if is_new:
        await message.answer(
            f"👋 Привет! Этот бот создан для получения файлов из моего Telegram-канала.\n"
            f"📎 Чтобы получить файл, подпишись на канал: [@externalzxc]({CHANNEL_LINK})\n\n"
            f"👋 Hello! This bot allows you to receive files from my Telegram channel.\n"
            f"📎 To get the file, please subscribe: [@externalzxc]({CHANNEL_LINK})",
            parse_mode='Markdown'
        )

    if not args or args not in files:
        return

    if await check_subscription(user_id):
        file_info = files[args]
        file_type = file_info['type']
        file_id = file_info['file_id']
        caption = f"📂 {file_info.get('name', 'Файл')}"

        if file_type == 'document':
            await bot.send_document(chat_id=message.chat.id, document=file_id, caption=caption)
        elif file_type == 'photo':
            await bot.send_photo(chat_id=message.chat.id, photo=file_id, caption=caption)
        elif file_type == 'video':
            await bot.send_video(chat_id=message.chat.id, video=file_id, caption=caption)
        elif file_type == 'audio':
            await bot.send_audio(chat_id=message.chat.id, audio=file_id, caption=caption)
        elif file_type == 'voice':
            await bot.send_voice(chat_id=message.chat.id, voice=file_id)
        elif file_type == 'animation':
            await bot.send_animation(chat_id=message.chat.id, animation=file_id, caption=caption)
        else:
            await message.answer("⚠️ Этот тип файла пока не поддерживается.")
    else:
        await message.answer(
            f"🚫 Вы не подписаны на канал!\n"
            f"🔗 Подпишитесь: [@externalzxc]({CHANNEL_LINK})\n\n"
            f"Затем нажмите ещё раз: /start {args}\n\n"
            f"🚫 You are not subscribed!\n"
            f"🔗 Please subscribe: [@externalzxc]({CHANNEL_LINK})\n"
            f"Then press again: /start {args}",
            parse_mode='Markdown'
        )

@dp.message_handler(content_types=types.ContentType.ANY)
async def handle_upload(message: types.Message):
    if message.from_user.id != OWNER_ID:
        return

    content_type = message.content_type
    file = None
    name = None

    if content_type == 'document':
        file = message.document.file_id
        name = message.document.file_name
    elif content_type == 'photo':
        file = message.photo[-1].file_id
        name = "photo.jpg"
    elif content_type == 'video':
        file = message.video.file_id
        name = message.video.file_name or "video.mp4"
    elif content_type == 'audio':
        file = message.audio.file_id
        name = message.audio.file_name or "audio.mp3"
    elif content_type == 'voice':
        file = message.voice.file_id
        name = "voice.ogg"
    elif content_type == 'animation':
        file = message.animation.file_id
        name = message.animation.file_name or "animation.gif"
    else:
        await message.answer("⚠️ Этот тип файла не поддерживается для реферальной отправки.")
        return

    key = str(uuid.uuid4())[:8]
    files[key] = {
        'file_id': file,
        'type': content_type,
        'name': name
    }
    save_files()

    bot_info = await bot.get_me()
    link = f"https://t.me/{bot_info.username}?start={key}"
    await message.answer(f"✅ Файл сохранён!\n📎 Ссылка: {link}")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    load_files()
    executor.start_polling(dp, skip_updates=True)
