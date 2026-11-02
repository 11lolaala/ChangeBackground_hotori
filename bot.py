from io import BytesIO
import asyncio
from aiogram import F, Bot, Dispatcher
from aiogram.types import BufferedInputFile, Message
import logic
from PIL import Image
import os
from aiogram.utils.media_group import MediaGroupBuilder

TOKEN = os.getenv("TOKEN")
bot = Bot(TOKEN)
dp = Dispatcher()
albums = {}


@dp.message(F.photo)
async def handle_photo(message):
    status = None
    try:
        if message.media_group_id:
            await collect_album(message)
            return
        status = await message.answer("Фото загрузилось, ожидайте обработку")
        result_photo = await process_one(message)
        if result_photo is None:
            await message.answer("Не получилось обработать фото")
            return
        await message.answer_photo(BufferedInputFile(result_photo, filename="result.png"))
    except Exception as e:
        print(f"Ошибка в handle_photo {e}")
        await message.answer("Что-то пошло не так")
    finally:
        if status:
            await status.delete()


async def collect_album(message):
    status = None
    try:
        gid = message.media_group_id
        is_first = gid not in albums
        if is_first:
            albums[gid] = []
        albums[gid].append(message)
        if not is_first:
            return
        await asyncio.sleep(2)
        messages = albums.pop(gid)
        status = await message.answer("Фотографии загрузились, ожидайте обработку")
        results = []
        for msg in messages:
            data = await process_one(msg)
            if data is not None:
                results.append(data)
        if len(results) == 0:
            await message.answer("Не удалось считать альбом фотографий")
            return
        builder = MediaGroupBuilder()
        for data in results:
            builder.add_photo(media=BufferedInputFile(data, filename="result.png"))
        await message.answer_media_group(builder.build())
    finally:
        if status:
            await status.delete()


async def process_one(msg):
    try:
        buf = BytesIO()
        await bot.download(msg.photo[-1], destination=buf)
        photo = Image.open(buf)
        result = await asyncio.to_thread(logic.process, photo)
        out = BytesIO()
        result.save(out, format="PNG")
        out.seek(0)
        return out.getvalue()
    except Exception as e:
        print(f"Ошибка в process_one: {e}")


async def main():
    await dp.start_polling(bot)


asyncio.run(main())
