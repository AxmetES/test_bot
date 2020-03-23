import os
import re
import pprint


def get_questions():
    with open('quiz-questions/1vs1200.txt', 'r', encoding='KOI8-R') as file:
        quiz_questions = file.read()
    questions = []
    answers = []

    # quiz = re.split('\n\n', quiz_questions)
    quiz = quiz_questions.split(2 * os.linesep)
    for quest in quiz:
        if 'Вопрос' in quest:
            questions.append(quest)
        elif 'Ответ' in quest:
            answers.append(quest)

    test = dict(zip(questions, answers))
    return test
