import fnmatch
import os
import os.path

import cv2
from PIL import Image
from aiogram import Dispatcher
from aiogram.types import Message, ContentType, InputFile
from pyffmpeg import FFmpeg

ff = FFmpeg()


async def user_start(message: Message):
    await message.answer("""🎥 Уникализатор Медиа ⚙️
📌   Этот бот был создан специально для уникализации креативов для Facebook/Google/YouTube

🤔 Что умеет этот бот: 

✅ Меняет исходный код видео.
✅ Накладывает невидимые элементы на видео.
✅ Меняет звуковую дорожку. 
✅ Удаляет метаданные.
✅ 99% захода креативов.
                        """)
    await message.answer("⚠️ Отправьте боту видео (MP4) или фото (JPEG) до 20МБ или с меньшим разрешением!")
    await message.answer("⚠⚠⚠️ Внимание! Одновременно можно обрабатывать не более 20 копий видео-файлов.")
    await message.answer("Если вы желаете оставить отзыв, то просто напишите его тут же и отправьте нам! 👇")


async def convert_media(message: Message):
    if message.content_type == "photo":
        await message.photo[-1].download()
        listOfFiles = os.listdir('./photos')
        pattern = "*.jpg"
        file = []
        for entry in listOfFiles:
            if fnmatch.fnmatch(entry, pattern):
                file.append(entry)
        photo = Image.open(f"./photos/{file[0]}")
        photo = photo.rotate(0.01)
        photo.save(f"./photos/{file[0]}")
        photo = InputFile(f"./photos/{file[0]}")
        await message.answer_photo(photo)
        await message.answer_document(InputFile(f"./photos/{file[0]}"))
        os.remove(f"./photos/{file[0]}")
    elif message.content_type == "video":
        await message.video.download()
        await message.answer("💤 Обработка началась!")
        listOfFiles = os.listdir('./videos')
        pattern_1 = "*.MP4"
        pattern_2 = "*.mp4"
        file = []
        for entry in listOfFiles:
            if fnmatch.fnmatch(entry, pattern_1):
                file.append(entry)
        if not file:
            for entry in listOfFiles:
                if fnmatch.fnmatch(entry, pattern_2):
                    file.append(entry)
        input_file = f"./videos/{file[0]}"
        vid = cv2.VideoCapture(input_file)
        width = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        ff.options(f"-i {input_file} -i transparent.png -filter_complex overlay=5:5 ./videos/video_transparent.mp4")
        if height > width:
            ff.options(f"-i {input_file} -vf scale=720:1280,setsar=1:1 -c:v libx264 ./videos/video.mp4")
            await message.answer_video(InputFile('./videos/video.mp4'))
        elif width > height:
            ff.options(
                f"-i ./videos/video_transparent.mp4 -vf scale=1280:720,setsar=1:1 -c:v libx264 ./videos/video.mp4")
            await message.answer_video(InputFile('./videos/video.mp4'))
        elif width == height:
            ff.options(
                f"-i ./videos/video_transparent.mp4 -vf scale=720:720,setsar=1:1 -c:v libx264 ./videos/video.mp4")
            await message.answer_video(InputFile('./videos/video.mp4'))
        os.remove(input_file)
        os.remove("./videos/video.mp4")
        os.remove("./videos/video_transparent.mp4")


def register_user(dp: Dispatcher):
    dp.register_message_handler(user_start, commands=["start"], state="*")
    dp.register_message_handler(convert_media, state="*", content_types=ContentType.ANY)
