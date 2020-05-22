import logging
import os
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
import random
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, RegexHandler
import quiz_questions
import redis
from dotenv import load_dotenv
from functools import partial

logger = logging.getLogger(__name__)

START_QUIZ, ANSWERING = range(2)


def start(bot, update):
    logger.info('bot is started')
    reply_keyboard = [['start quiz', 'cancel']]

    update.message.reply_text('Start quiz ?',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return START_QUIZ


def handle_new_question_request(r_conn, bot, update):
    files = quiz_questions.get_files(r_conn)
    quiz = quiz_questions.get_questions(files)
    reply_keyboard = [['surrender', 'cancel']]
    *keys, = quiz.keys()
    question = random.choice(keys)
    answer = quiz.get(question)
    chat_id = update.message.chat_id
    r_conn.set(f'tg-{chat_id}', answer)
    bot.send_message(chat_id=update.message.chat_id, text=question, reply_markup=ReplyKeyboardMarkup(reply_keyboard))
    return ANSWERING


def handle_solution_attempt(r_conn, bot, update):
    reply_keyboard = [['next', 'cancel']]
    text = update.message.text
    chat_id = update.message.chat_id
    db_answer = r_conn.get(f'tg-{chat_id}')
    answer = db_answer.decode('utf-8')
    if text == answer:
        text = 'Right!... next ?'
    else:
        text = f'Wrong!...\n Right answer:  {answer}\n next ?'

    update.message.reply_text(text,
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard))
    return START_QUIZ


def get_answer(r_conn, bot, update):
    reply_keyboard = [['next', 'cancel']]
    chat_id = update.message.chat_id
    db_answer = r_conn.get(f'tg-{chat_id}')
    answer = db_answer.decode('utf-8')
    update.message.reply_text(answer, reply_markup=ReplyKeyboardMarkup(reply_keyboard))

    return START_QUIZ


def cancel(bot, update):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def handle_error(update, context):
    logger.error(f'Update {update} caused error {context.error}')


def main():
    load_dotenv()

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    db_password = os.environ['DB_PASSWORD']
    db_port = os.environ['DB_PORT']
    db_URL = os.environ['DB_URL']
    token = os.getenv('TG_BOT_TOKEN')

    r_conn = redis.Redis(host=db_URL, db=0, port=db_port,
                         password=db_password)

    updater = Updater(token)
    dp = updater.dispatcher

    p_handle_new_question_request = partial(handle_new_question_request, r_conn)
    p_get_answer = partial(get_answer, r_conn)
    p_handle_solution_attempt = partial(handle_solution_attempt, r_conn)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            START_QUIZ: [
                RegexHandler('^start quiz', p_handle_new_question_request),
                RegexHandler('^next$', p_handle_new_question_request)],

            ANSWERING: [
                RegexHandler('^cancel$', cancel),
                RegexHandler('^surrender$', p_get_answer),
                MessageHandler(Filters.text, p_handle_solution_attempt)]
        },
        fallbacks=[RegexHandler('^cancel$', cancel)]
    )

    dp.add_error_handler(handle_error)
    dp.add_handler(conv_handler)
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
