#!/usr/bin/python3
# -*- coding: utf-8 -*-
import time
import os
import telebot
from moviepy.audio.io.AudioFileClip import AudioFileClip
from dotenv import load_dotenv, find_dotenv
from yandex_music import Client
import re

# Загрузка переменных окружения
load_dotenv(find_dotenv())
bot = telebot.TeleBot(os.getenv('TELEGRAMM_TOKEN'))
client = Client(token=os.getenv('YA_TOKEN'))
client.init()


@bot.message_handler(commands=['start'])
def start_message(message):
    """Приветственное сообщение."""
    mess = "Привет! Я могу вырезать фрагмент из трека. Используй команду /sample, чтобы начать."
    bot.send_message(message.chat.id, mess)


@bot.message_handler(commands=['sample'])
def sample_command(message):
    """Обрабатывает команду /sample."""
    msg = bot.send_message(message.chat.id, "Скинь ссылку на трек (в формате mp3).")
    bot.register_next_step_handler(msg, get_track_url)


def get_track_url(message):
    """Получает ссылку на трек от пользователя."""
    track_url = message.text.strip()
    bot.send_message(message.chat.id, "Отлично! Укажи начальное время фрагмента в формате MM:SS.")
    bot.register_next_step_handler(message, get_start_time, track_url)


def get_start_time(message, track_url):
    """Получает начальное время фрагмента."""
    try:
        start_time = parse_time(message.text.strip())
        bot.send_message(message.chat.id, "Теперь укажи конечное время фрагмента в формате MM:SS.")
        bot.register_next_step_handler(message, get_end_time, track_url, start_time)
    except ValueError:
        msg = bot.send_message(message.chat.id, "Ошибка! Укажи время в правильном формате MM:SS.")
        bot.register_next_step_handler(msg, get_start_time, track_url)


def get_end_time(message, track_url, start_time):
    """Получает конечное время фрагмента."""
    try:
        end_time = parse_time(message.text.strip())
        bot.send_message(message.chat.id, "Начинаю обработку трека, подожди немного...")
        download_and_cut_track(message.chat.id, track_url, start_time, end_time)
    except ValueError:
        msg = bot.send_message(message.chat.id, "Ошибка! Укажи время в правильном формате MM:SS.")
        bot.register_next_step_handler(msg, get_end_time, track_url, start_time)


def parse_time(time_str):
    """Парсит строку времени формата MM:SS в секунды."""
    parts = time_str.split(":")
    if len(parts) != 2:
        raise ValueError("Неверный формат времени.")
    minutes, seconds = map(int, parts)
    return minutes * 60 + seconds


def download_and_cut_track(chat_id, track_url, start_time, end_time):
    """Скачивает трек, вырезает фрагмент и отправляет его пользователю."""
    try:
        match = re.search(r"album/(\d+)/track/(\d+)", track_url)
        album_id, track_id = match.groups()
        idTrack = [f"{album_id}:{track_id}"]
        track_path = "temp_track.mp3"
        # Скачивание трека
        track = client.tracks(track_id)
        track_info = client.tracks_download_info(track_id=track_id, get_direct_links=True)
        track_name = track[0].title.encode('utf-8').decode('utf-8')
        track_name = "sample"
        track_info.sort(reverse=True, key=lambda key: key['bitrate_in_kbps'])
        client.request.download(url=track_info[0]['direct_link'],
                filename=track_path
            )

        # Вырезание фрагмента
        output_path = f"{track_name}.mp3"
        with AudioFileClip(track_path) as audio:
            cut = audio.subclipped(start_time, end_time)
            cut.write_audiofile(output_path)

        # Отправка файла пользователю
        with open(output_path, "rb") as f:
            bot.send_audio(chat_id, f)

        # Удаление временных файлов
        os.remove(track_path)
        os.remove(output_path)

    except Exception as e:
        bot.send_message(chat_id, f"Ошибка при обработке трека: {e}")


if __name__ == '__main__':
    bot.infinity_polling()
