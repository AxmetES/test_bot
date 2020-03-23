import logging
import os
import numpy
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import random
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from quiz_questions import get_questions
import redis

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

db_password = os.getenv('DB_PASSWORD')
db_port = os.getenv('DB_PORT')
db_URL = os.getenv('DB_URL')


def start(bot, update):
    test = get_questions()

    question = random.choice(list(test.keys()))
    answer = test.get(question)

    keyboard = [[InlineKeyboardButton("{button_1}", callback_data='1'),
                 InlineKeyboardButton("{button_2}", callback_data='2')],
                [InlineKeyboardButton("{button_3}", callback_data='3')]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    chat_id = update.message.chat_id
    r_conn.set(chat_id, question)
    r_conn.set(chat_id, answer)
    print(answer)
    update.message.reply_text(f'{question}:', reply_markup=reply_markup)


def button(bot, update):
    query = update.callback_query
    chat_id = str(query['message']['chat']['id'])
    db_question = r_conn.get(chat_id)
    query.edit_message_text(text=f"{db_question}".format(query.data))


def echo(bot, update):
    message = update.message.text
    chat_id = update.message.chat_id
    db_answer = r_conn.get(chat_id)
    answer = str(db_answer.decode('utf-8'))
    answer = answer.replace('Ответ:', '')
    print(answer)
    if message in answer:
        bot.send_message(chat_id=update.message.chat_id, text="Right")
    else:
        bot.send_message(chat_id=update.message.chat_id, text='Wrong')


def main():
    token = os.getenv('BOT_TOKEN')
    updater = Updater(token)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(MessageHandler(Filters.text, echo))
    updater.start_polling()
    logger.info('bot is started')

    updater.idle()


if __name__ == '__main__':
    r_conn = redis.Redis(host=db_URL, db=0, port=db_port,
                         password=db_password, charset='utf-8')
    main()
