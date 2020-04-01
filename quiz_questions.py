import os


def get_files():
    directory = 'quiz-questions/'
    files = os.listdir(directory)
    files_txt = filter(lambda x: x.endswith('.txt'), files)
    return files_txt


def get_questions():
    test = {}
    key = val = None
    files_txt = get_files()
    for txt in files_txt:
        with open(f'quiz-questions/{txt}', 'r', encoding='KOI8-R') as file:
            quiz_questions = file.read()

        quiz = quiz_questions.split('\n\n\n')

        for quiz_quest in quiz:
            for quest in quiz_quest.split('\n\n'):
                if quest.startswith('Вопрос'):
                    key = quest
                elif quest.startswith('Ответ'):
                    val = quest
                elif key and val:
                    test.update({key: val})

    return test
