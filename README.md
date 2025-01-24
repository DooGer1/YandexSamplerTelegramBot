# Yandex Sampler Telegram Bot


Программа для скачивания семпла с яндекс музыки через интерфейс телеграмм бота

Для работы необходимо:
1. [Токен вашего яндекс аккаунта](https://github.com/MarshalX/yandex-music-api/discussions/513#discussioncomment-2729781)
2. [Токен телеграмм вашего бота](https://lifehacker.ru/kak-sozdat-bota-v-telegram/)

# Установка
## Linux / MacOS / Windows
    1. запустить терминал // для Linux/MacOS
    2. git clone 'THIS_PROJECT'
    3. cd 'THIS_PROJECT'
    4. pip install -r requirements.txt
    5. nano .env
______________ 
#### .env

    TELEGRAMM_TOKEN=YOUR_TOKEN
    YA_TOKEN=YOUR_TOKEN
______________

    6. python tbot.py

1. Отправьте команду вашему телеграм боту:

    /sample - обзор существующих команд


2. Отправьте ссылку на музыку из Яндекс Музыки.
3. Укажите время начала отрезка семпла
4. Укажите время окончания отрезка семпла

Музыка скачивается в максимальном доступном качестве до 320 kbps.

