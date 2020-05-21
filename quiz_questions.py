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
            loaded_text = file.read()

        questions = loaded_text.split('\n\n\n')

        for quiz_question in questions:
            for query in quiz_question.split('\n\n'):
                if query.startswith('Вопрос'):
                    question = query.split('\n')
                    del question[0]
                    question = ''.join(question)
                elif query.startswith('Ответ'):
                    answer = query.replace('Ответ:\n', '').replace('\n', '')
                    test.update({question: answer})

    return test

