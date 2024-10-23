import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import requests
import base64

from youtubesearchpython import *


import youtube_dl

# Команда /start
def start(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    # Кнопки для части команд
    keyboard = [['/repo']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    # Приветственное сообщение
    update.message.reply_text(
        f'Привет, {user.first_name}! Я бот, который может отправлять изображения и аудиофайлы по запросу. Команды /image и /audio',
        reply_markup=reply_markup
    )
   
# Команда для получения изображения
def image(update: Update, context: CallbackContext) -> None:
    if len(context.args) > 0:
        promt = ''
        for word in context.args:
            promt += word + ', '
        url = "http://127.0.0.1:7860"
        payload = {
            "prompt":promt,
            "steps": 20
        }
        # Send said payload to said URL through the API.
        response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload)
        r = response.json()
        # Decode and save the image.
        with open("output.png", 'wb') as f:
            f.write(base64.b64decode(r['images'][0]))
        context.bot.send_message(chat_id=update.effective_chat.id, text=f'Photo:')
        context.bot.send_photo(chat_id=update.effective_chat.id, photo=open('output.png', 'rb'))
    else:
        update.message.reply_text('Пожалуйста, введите название изображения после команды /image. Пример: /image example')

# Команда для получения аудиофайла
def audio(update: Update, context: CallbackContext) -> None:
    if len(context.args) > 0:
        audio_name = ''
        for word in context.args:
            audio_name += word + ' '
        audio_name +='Trailer'

        customSearch = CustomSearch(audio_name,  SearchMode.videos)
        res = customSearch.result()
        url = customSearch.resultComponents[0]['link']

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        update.message.reply_text(url)
        #with youtube_dl.YoutubeDL(ydl_opts) as ydl:
           # ydl.download([url])
    else:
        update.message.reply_text('Пожалуйста, введите название аудиофайла после команды /audio. Пример: /audio example')


# Команда для получения ссылки на репозиторий
def repo(update: Update, context: CallbackContext) -> None:
    # Кнопка с ссылкой на репозиторий
    keyboard = [[InlineKeyboardButton("Ссылка на репозиторий", url="https://github.com/reatpig/TelegramBot")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    update.message.reply_text('Нажмите на кнопку, чтобы перейти в репозиторий:', reply_markup=reply_markup)

# Обработка сообщений без команды
def echo(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(f"Вы написали: {update.message.text}. Для списка команд используйте /start")

def main():
    # Вставьте ваш токен
    updater = Updater("6974824210:AAErzSnUYXeUgkMJC97UZcmlcytUch42xrI", use_context=True)

    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher

    # Обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("image", image))
    dp.add_handler(CommandHandler("audio", audio))
    dp.add_handler(CommandHandler("repo", repo))

    # Обработчик для текстовых сообщений
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Запуск бота
    updater.start_polling()

    # Ожидание завершения
    updater.idle()

if __name__ == '__main__':
    main()