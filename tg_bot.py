import logging
import os
import numpy
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
import random
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler, \
    RegexHandler
from quiz_questions import get_questions
import redis

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

START_QUIZ, ANSWER = range(2)

db_password = os.getenv('DB_PASSWORD')
db_port = os.getenv('DB_PORT')
db_URL = os.getenv('DB_URL')


def start(bot, update):
    reply_keyboard = [['start quiz', 'cancel']]

    update.message.reply_text('Start quiz ?',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return START_QUIZ


def handle_new_question_request(bot, update):
    test = get_questions()
    question = random.choice(list(test.keys()))
    answer = test.get(question)
    print(answer)
    chat_id = update.message.chat_id
    r_conn.set(chat_id, question)
    r_conn.set(chat_id, answer)
    bot.send_message(chat_id=update.message.chat_id, text=question)
    return ANSWER


def handle_solution_attempt(bot, update):
    reply_keyboard = [['next', 'cancel']]
    text = update.message.text
    chat_id = update.message.chat_id
    db_answer = r_conn.get(chat_id)
    answer = str(db_answer.decode('utf-8'))
    answer = answer.replace('Ответ:', '')
    print(answer)
    print(text)
    if text in answer:
        text = 'Right! next ?'
    else:
        text = 'Wrong! next ?'

    update.message.reply_text(text,
                              reply_keyboard=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return START_QUIZ


def cancel(bot, update):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def main():
    token = os.getenv('BOT_TOKEN')
    updater = Updater(token)

    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            START_QUIZ: [MessageHandler(Filters.text, handle_new_question_request)],

            ANSWER: [MessageHandler(Filters.text, handle_solution_attempt),
                     RegexHandler('next', handle_solution_attempt)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    dp.add_handler(conv_handler)
    updater.start_polling()
    logger.info('bot is started')

    updater.idle()


if __name__ == '__main__':
    r_conn = redis.Redis(host=db_URL, db=0, port=db_port,
                         password=db_password, charset='utf-8')
main()
