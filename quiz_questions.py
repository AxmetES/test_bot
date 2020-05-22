import os
import glob
import redis
from dotenv import load_dotenv
import argparse

load_dotenv()


def get_directory(default_dir):
    parser = argparse.ArgumentParser(description='Add directory, default directory from ".env".')
    parser.add_argument('-l', '--directory', type=str, default=default_dir)
    args = parser.parse_args()
    return args


def get_files(r_conn):
    files = []
    directory = r_conn.get('directory')
    os.chdir(directory)
    for file in glob.glob('*.txt'):
        files.append(file)
    return files


def get_questions(files):
    test = {}
    question = answer = None
    files_txt = files
    for txt in files_txt:
        with open(os.path.join(os.getcwd(), txt), 'r', encoding='KOI8-R') as file:
            loaded_text = file.read()

        questions = loaded_text.split('\n\n\n')
        for quiz_question in questions:
            for query in quiz_question.split('\n\n'):
                if query.startswith('Вопрос'):
                    question = query.split('\n')
                    del question[0]
                    question = ''.join(question)
                elif query.startswith('Ответ'):
                    answer = query.replace('Ответ:\n', ' ').replace('\n', ' ')
                    test[question] = answer

    return test


if __name__ == '__main__':
    db_password = os.environ['DB_PASSWORD']
    db_port = os.environ['DB_PORT']
    db_URL = os.environ['DB_URL']
    default_dir = os.getenv('DIR')

    r_conn = redis.Redis(host=db_URL, db=0, port=db_port,
                         password=db_password)

    args = get_directory(default_dir)
    r_conn.set('directory', args.directory)
