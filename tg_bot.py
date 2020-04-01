import logging
import os
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
import random
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, RegexHandler
from quiz_questions import get_questions
import redis
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
test = get_questions()

START_QUIZ, ANSWERING = range(2)

db_password = os.environ['DB_PASSWORD']
db_port = os.environ['DB_PORT']
db_URL = os.environ['DB_URL']

logger.info(db_password)
logger.info(db_port)
logger.info(db_URL)


def start(bot, update):
    reply_keyboard = [['start quiz', 'cancel']]

    update.message.reply_text('Start quiz ?',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return START_QUIZ


def handle_new_question_request(bot, update):
    reply_keyboard = [['surrender', 'cancel']]

    question = random.choice(list(test.keys()))
    answer = test.get(question)
    chat_id = update.message.chat_id
    r_conn.set(chat_id, answer)
    bot.send_message(chat_id=update.message.chat_id, text=question, reply_markup=ReplyKeyboardMarkup(reply_keyboard))
    return ANSWERING


def handle_solution_attempt(bot, update):
    reply_keyboard = [['next', 'cancel']]
    text = update.message.text
    chat_id = update.message.chat_id
    db_answer = r_conn.get(chat_id)
    answer = str(db_answer.decode('utf-8'))
    answer = answer.replace('Ответ:', '')
    if text in answer:
        text = 'Right!... next ?'
    else:
        text = 'Wrong!... next ?'

    update.message.reply_text(text,
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard))

    return START_QUIZ


def get_answer(bot, update):
    reply_keyboard = [['next', 'cancel']]
    chat_id = update.message.chat_id
    db_answer = r_conn.get(chat_id)
    answer = str(db_answer.decode('utf-8'))
    answer = answer.replace('Ответ:', '')
    update.message.reply_text(answer, reply_markup=ReplyKeyboardMarkup(reply_keyboard))

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
            START_QUIZ: [RegexHandler('^start quiz', handle_new_question_request),
                         RegexHandler('^next$', handle_new_question_request)],

            ANSWERING: [RegexHandler('^cancel$', cancel),
                        RegexHandler('^surrender$', get_answer),
                        MessageHandler(Filters.text, handle_solution_attempt)]
        },
        fallbacks=[RegexHandler('^cancel$', cancel)]
    )
    dp.add_handler(conv_handler)
    updater.start_polling()
    logger.info('bot is started')

    updater.idle()


if __name__ == '__main__':
    r_conn = redis.Redis(host=db_URL, db=0, port=db_port,
                         password=db_password, charset='utf-8')
    main()
