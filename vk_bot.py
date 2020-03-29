import redis
import vk_api
import logging
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
from dotenv import load_dotenv
import os
from quiz_questions import get_questions
import random

load_dotenv()

logger = logging.getLogger('dialogflow_bot_logger')


def send_message(vk_api, text, user_id):
    vk_api.messages.send(
        user_id=user_id,
        message=text,
        random_id=get_random_id()
    )


def handle_new_question_request(vk_api, user_id, question_keyboard):
    test = get_questions()
    question = random.choice(list(test.keys()))
    answer = test.get(question)
    r_conn.set(user_id, answer)
    vk_api.messages.send(
        user_id=user_id,
        message=question,
        random_id=get_random_id(),
        keyboard=question_keyboard.get_keyboard()
    )


def handle_solution_attempt(vk_api, user_id, solution_keyboard, event):
    db_answer = r_conn.get(user_id)
    answer = str(db_answer.decode('utf-8'))
    user_text = event.text
    if user_text in answer:
        answer = 'Right! Next ?'
    else:
        answer = 'Wrong! Next ?'
    vk_api.messages.send(
        user_id=user_id,
        message=answer,
        random_id=get_random_id(),
        keyboard=solution_keyboard.get_keyboard()
    )


def surrender(vk_api, user_id, solution_keyboard):
    db_answer = r_conn.get(user_id)
    answer = str(db_answer.decode('utf-8'))
    vk_api.messages.send(
        user_id=user_id,
        message=answer,
        random_id=get_random_id(),
        keyboard=solution_keyboard.get_keyboard()
    )


def cancel(vk_api, user_id, start_keyboard):
    vk_api.messages.send(
        user_id=user_id,
        message='Bay Bay',
        random_id=get_random_id(),
        keyboard=start_keyboard.get_keyboard()
    )


if __name__ == "__main__":
    db_URL = os.getenv('DB_URL')
    db_port = os.getenv('DB_PORT')
    db_password = os.getenv('DB_PASSWORD')
    vk_token = os.getenv('VK_GROUP_KEY')

    r_conn = redis.Redis(host=db_URL, db=0, port=db_port,
                         password=db_password, charset='utf-8')

    solution_keyboard = VkKeyboard(one_time=True)
    solution_keyboard.add_button('next', color=VkKeyboardColor.POSITIVE)
    solution_keyboard.add_button('cancel', color=VkKeyboardColor.POSITIVE)

    question_keyboard = VkKeyboard(one_time=True)
    question_keyboard.add_button('surrender', color=VkKeyboardColor.POSITIVE)
    question_keyboard.add_button('cancel', color=VkKeyboardColor.POSITIVE)

    start_keyboard = VkKeyboard(one_time=True)
    start_keyboard.add_button('Начать', color=VkKeyboardColor.POSITIVE)

    vk_session = vk_api.VkApi(token=vk_token)
    vk_api = vk_session.get_api()

    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger.setLevel(logging.DEBUG)

    longpoll = VkLongPoll(vk_session)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            user_id = event.user_id
            if event.text == 'Начать':
                handle_new_question_request(vk_api, user_id, question_keyboard)
            elif event.text == 'next':
                handle_new_question_request(vk_api, user_id, question_keyboard)
            elif event.text == 'surrender':
                surrender(vk_api, user_id, solution_keyboard)
            elif event.text == 'cancel':
                cancel(vk_api, user_id, start_keyboard)
            elif event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                handle_solution_attempt(vk_api, user_id, solution_keyboard, event)
