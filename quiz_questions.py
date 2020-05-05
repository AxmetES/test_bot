import os


def get_files():
    directory = 'quiz-questions'
    files = os.listdir(directory)
    files_txt = filter(lambda x: x.endswith('.txt'), files)
    return files_txt


def get_questions():
    directory = 'quiz-questions'
    test = {}
    question = answer = None
    files_txt = get_files()
    for txt in files_txt:
        with open(os.path.join(directory, txt), 'r', encoding='KOI8-R') as file:
            questions = file.read()

        questions = questions.split('\n\n\n')

        for quiz_question in questions:
            for query in quiz_question.split('\n\n'):
                if query.startswith('Вопрос'):
                    question = query
                elif query.startswith('Ответ'):
                    answer = query
                elif question and answer:
                    test.update({question: answer})

    return test
