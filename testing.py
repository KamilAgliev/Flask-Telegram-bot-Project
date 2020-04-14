from data.english_data import WORDS_FOR_LEARNING
from data.questions import Question
cnt = 1
for section in WORDS_FOR_LEARNING.keys():
    for les in WORDS_FOR_LEARNING[section]['themes']:
        for word in les['words']:
            # ques = Question(
            #     id=cnt,
            #     theme=les['title'],
            #     answer=word[]
            # )
            cnt += 1
