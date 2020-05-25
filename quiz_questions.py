import os
import glob
import redis
from dotenv import load_dotenv
import argparse


def get_directory(default_dir):
    parser = argparse.ArgumentParser(description='Add directory, default directory from ".env".')
    parser.add_argument('-l', '--directory', type=str, default=default_dir)
    args = parser.parse_args()
    return args


def get_files(directory):
    files = [file for file in glob.glob(os.path.join(directory, '*.txt'))]
    return files


def get_questions(files):
    test = {}
    question = answer = None
    files_txt = files
    for txt in files_txt:
        with open(txt, 'r', encoding='KOI8-R') as file:
            loaded_text = file.read()

        questions = loaded_text.split('\n\n\n')
        for quiz_question in questions:
            for query in quiz_question.split('\n\n'):
                if query.startswith('Вопрос'):
                    question = query.split('\n')
                    del question[0]
                    question = ''.join(question)
                elif query.startswith('Ответ'):
                    answer = query.replace('Ответ:\n', ' ').replace('\n', ' ').replace('\n', '')
                    test[question] = answer

    return test


if __name__ == '__main__':
    load_dotenv()
    dic = os.getenv('DIR')
    files = get_files(dic)
    print(get_questions(files))
