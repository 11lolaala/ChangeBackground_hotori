from io import BytesIO
import asyncio
from aiogram import F, Bot, Dispatcher
from aiogram.types import BufferedInputFile, Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

import logic
from PIL import Image
import os
from aiogram.utils.media_group import MediaGroupBuilder

TOKEN = os.getenv("TOKEN")
bot = Bot(TOKEN)
dp = Dispatcher()
albums = {}
ready_albums = {}
kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Сделать белый фон", callback_data="white")],
    [InlineKeyboardButton(text="Сделать фон для хотори", callback_data="hotori")],
]
)


@dp.message(F.photo)
async def handle_photo(message):
    status = None
    try:
        if message.media_group_id:
            await collect_album(message)
            return
        await message.reply("Выбери фон:", reply_markup=kb)
        return
    except Exception as e:
        print(f"Ошибка в handle_photo {e}")
        await message.answer("Что-то пошло не так")
    finally:
        if status:
            await status.delete()


@dp.callback_query(F.data.in_({"hotori", "white"}))
async def handle_choice(callback: CallbackQuery):
    status = None
    photo_msg = callback.message.reply_to_message
    if photo_msg is None:
        await callback.answer("Фото не найдено")
        return
    try:
        await callback.answer("Принято")
        await callback.message.delete()
        status = await photo_msg.answer("Ожидайте обработку")
        result = await process_one(photo_msg, callback.data)
        if result is None:
            await photo_msg.answer("Не удалось обработать фото")
            return
        await photo_msg.answer_photo(BufferedInputFile(result, filename="result.png"))
    except Exception as e:
        await photo_msg.answer("Что-то пошло не так, попробуйте снова")
        print(f"Ошибка в handle_choice: {e}")
    finally:
        if status:
            await status.delete()


async def collect_album(message):
    gid = message.media_group_id
    is_first = gid not in albums
    if is_first:
        albums[gid] = []
    albums[gid].append(message)
    if not is_first:
        return
    await asyncio.sleep(2)
    messages = albums.pop(gid)
    ready_albums[gid] = messages
    kb_album = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Сделать белый фон", callback_data=f"album:white:{gid}")],
        [InlineKeyboardButton(text="Сделать фон для хотори", callback_data=f"album:hotori:{gid}")],
    ])
    await message.reply("Выбери фон:", reply_markup=kb_album)


@dp.callback_query(F.data.startswith("album:"))
async def handle_album_choice(callback: CallbackQuery):
    parts = callback.data.split(":")
    mode = parts[1]
    gid = parts[2]

    messages = ready_albums.pop(gid, None)
    if messages is None:
        await callback.answer("Альбом не найден")
        return

    await callback.answer("Принято")
    await callback.message.delete()

    first = messages[0]
    status = None
    try:
        status = await first.answer("Фотографии загрузились, ожидайте обработку")

        results = []
        for msg in messages:
            data = await process_one(msg, mode)
            if data is not None:
                results.append(data)

        if len(results) == 0:
            await first.answer("Не удалось обработать фото")
            return

        builder = MediaGroupBuilder()
        for data in results:
            builder.add_photo(media=BufferedInputFile(data, filename="result.png"))
        await first.answer_media_group(builder.build())
    except Exception as e:
        print(f"Ошибка в handle_album_choice: {e}")
        await first.answer("Что-то пошло не так, попробуйте снова")
    finally:
        if status:
            await status.delete()


async def process_one(msg, mode):
    try:
        buf = BytesIO()
        await bot.download(msg.photo[-1], destination=buf)
        photo = Image.open(buf)
        if mode == "white":
            result = await asyncio.to_thread(logic.process_white, photo)
        else:
            result = await asyncio.to_thread(logic.process_hotori_base, photo)
        out = BytesIO()
        result.save(out, format="PNG")
        out.seek(0)
        return out.getvalue()
    except Exception as e:
        print(f"Ошибка в process_one: {e}")
        await msg.answer(f"Ошибка: {e}")


async def main():
    await dp.start_polling(bot)


asyncio.run(main())
