import os
import asyncio
import threading

from pyrogram import Client, filters
from pyrogram.types import Message

import moviepy.editor as mpy
from moviepy.video.fx.all import crop

from core import Module, Author

module = Module(
    name='string_id=module_name',
    description='string_id=description',
    authors=Author('pelmeshke', telegram_username='pelmeshke', job='string_id=author_creator'),
    version='v1.0',
    release_date='11-08-2024',
    strings={
        'ru': {
            'module_name': 'Кружочкер',
            'description': r'Берет видео и делает из него кружочек ¯\_(ツ)_/¯',
            'author_creator': 'Создатель',
            'there_is_no_reply': 'Ответьте на сообщение с видео, чтобы сделать из него кружочек',
            'too_long_duration': 'Длительность видео не должна быть больше минуты',
            'downloading': 'Загрузка...',
            'cropping': 'Обрезка видео',
            'sending': 'Отправка...',

        },
        'en': {
            'module_name': 'VideoNoteMaker',
            'description': r'Takes video and makes a video note from it ¯\_(ツ)_/¯',
            'author_creator': 'Creator',
            'there_is_no_reply': 'Reply to message with video to make a video note from it',
            'too_long_duration': 'A video duration must be no longer than a minute',
            'downloading': 'Download...',
            'cropping': 'Cropping',
            'sending': 'Sending...',
        },
    },
    requirements=['moviepy']

)


@Client.on_message(filters.command("videonotemake") & filters.me)
async def videonotemaker(_, message: Message):
    reply: Message = message.reply_to_message
    if not reply or not reply.video:
        await message.reply(message.get_string('there_is_no_reply'))
        return

    if reply.video.duration >= 60:
        await message.reply(message.get_string('too_long_duration'))
        return

    bot_message = await message.reply(message.get_string('downloading'))

    video_file = await reply.download()
    filename = os.path.split(video_file)[-1]
    new_filename = 'cropped_' + filename
    new_video_file = os.path.join(*os.path.split(video_file)[:-1], new_filename)

    thread = threading.Thread(target=crop_video, args=(video_file, new_video_file))
    thread.start()

    counter = 0
    while thread.is_alive():
        await bot_message.edit(message.get_string('cropping') + '.' * (counter + 1))
        counter = (counter + 1) % 3
        await asyncio.sleep(1)

    await bot_message.edit(message.get_string('sending'))
    await message.reply_video_note(new_video_file)
    await bot_message.delete()

    try:
        os.remove(video_file)
        os.remove(new_video_file)
    except OSError:
        pass


def crop_video(video_file, new_filename):
    clip = mpy.VideoFileClip(video_file)
    (w, h) = clip.size
    cropped_clip = crop(clip, width=min(w, h, 480), height=min(w, h, 480), x_center=w / 2, y_center=h / 2)
    cropped_clip.write_videofile(new_filename, codec="libx264")
