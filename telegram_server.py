"""MyEng - Телеграм бот для узучения английского языка"""
import datetime
import random

import requests
from flask import Flask, render_template, jsonify
import datetime
from flask import Flask, render_template, request
from flask_login import LoginManager, login_user, logout_user, \
    login_required
from flask_restful import Resource, Api, reqparse
from flask_wtf import FlaskForm
from requests import post, get, delete
from telegram import ReplyKeyboardMarkup
from werkzeug.exceptions import abort
from werkzeug.utils import redirect
from wtforms import PasswordField, BooleanField, SubmitField, StringField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
from flask import make_response
from data import db_session
from data.users import User
from flask_server import RegisterForm

from data.telegram_bot_data import TOKEN_FOR_TELEGRAM_BOT
# Импортируем необходимые классы.
from telegram.ext import Updater, MessageHandler, Filters, ConversationHandler
from telegram.ext import CallbackContext, CommandHandler
from data.telegram_bot_data import sessionStorage

reply_keyboard = [["1000 слов на английском - 80 % английского"],
                  ["сериал Friends"],
                  ["Сериалы с субтитрами"],
                  ["Аудирование"],
                  ["Чтение"],
                  ["Грамматика"],
                  ["Фонетика"],
                  ["Общение"],
                  ["Видеоканалы"],
                  ["Порталы для самостоятельного изучения"],
                  ["назад"]]
other_links_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
reply_keyboard = [["Английский для туристов в дороге"],
                  ["Английский в гостинице"],
                  ["Исследуем город"],
                  ["Английский для туристов в ресторане"],
                  ["Английский для туристов в магазине"],
                  ["Основные термины бизнеса"],
                  ["Фразы на английском, которые касаются работы производства"],
                  ["Лексика для маркетинга, рекламы и продаж"],
                  ["Финансовая тематика"],
                  ["Полезные фразы для собеседования на английском"],
                  ["Слушать и слышать!"],
                  ["Чтение на английском"],
                  ["Старый друг лучше новых двух?"],
                  ["Переносим всю свою жизнь на английский язык!"],
                  ["Рекомендации для тех, кто хочет хорошо говорить на английском"],
                  ['назад']]
themes_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
reply_keyboard = [["Английский для туристов в дороге"],
                  ["Английский в гостинице"],
                  ["Исследуем город"],
                  ["Английский для туристов в ресторане"],
                  ["Английский для туристов в магазине"],
                  ["Основные термины бизнеса"],
                  ["Фразы на английском, которые касаются работы производства"],
                  ["Лексика для маркетинга, рекламы и продаж"],
                  ["Финансовая тематика"],
                  ["Полезные фразы для собеседования на английском"],
                  ["Слушать и слышать!"],
                  ["Чтение на английском"],
                  ["Старый друг лучше новых двух?"],
                  ["Переносим всю свою жизнь на английский язык!"],
                  ["Рекомендации для тех, кто хочет хорошо говорить на английском"],
                  ['начать тест'],
                  ['назад']]
themes_markup_beg_test = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
reply_keyboard = [['путешествия'],
                  ['для работы за границей'],
                  ['разговорный'],
                  ["путешествия, для работы за границей"],
                  ["путешествия, разговорный"],
                  ["для работы за границей, разговорный"],
                  ["путешествия, для работы за границей, разговорный"]]
aims_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


def register(update, context):
    mes = update.message.text.strip()
    user_id = update.message.from_user.id
    res = get(f"http://localhost:5000/api/users/{user_id}").json()
    if res["message"] == 'ok':
        update.message.reply_text("У вас уже есть аккаунт!")
        sessionStorage[user_id]["login_stage"] = 0
        return login(update, context)
    else:
        if user_id not in sessionStorage.keys():
            form = RegisterForm()
            sessionStorage[user_id] = {
                "register_stage": 0,
                "reg_form": form,
            }
            update.message.reply_text("Hello, я - телеграм бот Myeng."
                                      "\nЗдесь вы можете изучать английский по разделам,"
                                      "\nсмотреть полезную информацию на разным темам,"
                                      "\nувидеть интересные ссылки для изучения анлийского,"
                                      "\nзнания тут закрепляються с помощью разных тестов по словам темы."
                                      "\nТакже у меня есть встроенный переводчик, который доступен в любой момент!"
                                      "\nИзучать английский интресно и весело!Вперед!")
    stage = sessionStorage[user_id]['register_stage']
    if stage != len(RegisterForm.stages):
        if stage != 0:
            if stage == 1:
                sessionStorage[user_id]["reg_form"].name = mes
            if stage == 2:
                sessionStorage[user_id]["reg_form"].surname = mes
            if stage == 3:
                if "@" not in mes:
                    update.message.reply_text("email должен содержать символ '@' !")
                    return 1
                sessionStorage[user_id]["reg_form"].email = mes
            if stage == 4:
                if len(mes) < 8:
                    update.message.reply_text("Пароль должен состоять \n "
                                              "как минимум из 8 символом")
                    return 1
                sessionStorage[user_id]["reg_form"].password = mes
            if stage == 5:
                if mes != sessionStorage[user_id]["reg_form"].password:
                    update.message.reply_text("Пароли должны совпадать!")
                    return 1
                sessionStorage[user_id]["reg_form"].password_again = mes
            if stage == 6:
                sessionStorage[user_id]["reg_form"].age = int(mes)
            if stage == 7:
                sessionStorage[user_id]["reg_form"].address = mes
        update.message.reply_text(RegisterForm.stages[stage])
        sessionStorage[user_id]['register_stage'] += 1
        return 1
    sessionStorage[user_id]["reg_form"].aim = ""
    for section in mes.lower().split(','):
        section = section.lower().strip()
        if len(section) == 0:
            continue
        if section not in ['путешествия', 'для работы за границей', 'разговорный']:
            update.message.reply_text(
                "Выберите цели из предложенных! (путешествия, для работы за границей, разговорный)."
                "\nЕсли целей много, то вводите их через запятую(,)")
            return 1
        else:
            sessionStorage[user_id]["reg_form"].aim += section + ','
    sessionStorage[user_id]['reg_form'].aim = sessionStorage[user_id]['reg_form'].aim[:-1]
    data = sessionStorage[user_id]["reg_form"]
    a = True
    try:
        nick = update.message.from_user.username
    except Exception:
        a = False
    if a:
        res = post('http://localhost:5000/api/users', json={
            'id': user_id,
            'name': data.name,
            'surname': data.surname,
            'email': data.email,
            'password': data.password,
            'address': data.address,
            'age': data.age,
            'aim': data.aim,
            'telegram_name': nick,
        }).json()
    else:
        res = post('http://localhost:5000/api/users', json={
            'id': user_id,
            'name': data.name,
            'surname': data.surname,
            'email': data.email,
            'password': data.password,
            'address': data.address,
            'age': data.age,
            'aim': data.aim,
            'telegram_name': "",
        }).json()
    print(res)
    sessionStorage[user_id]["login_stage"] = 0
    update.message.reply_text("Вы успешно зарегестрированы!")
    return learning(update, context)


def login(update, context):
    mes = update.message.text.strip()
    user_id = update.message.from_user.id
    if sessionStorage[user_id]['login_stage'] == 0:
        update.message.reply_text("Введите пароль от вашего аккаунта")
        sessionStorage[user_id]['login_stage'] += 1
        return 2
    else:
        given_password = mes
        res = get(f"http://localhost:5000/api/users/{user_id}").json()
        if res['message'] == "ok":
            ses = db_session.create_session()
            user = ses.query(User).filter(User.id == user_id).first()
            if user and user.check_password(given_password):
                sessionStorage[user_id]['login_stage'] = 0
                return learning(update, context)
            else:
                update.message.reply_text(
                    "Введены неправильные данные, введите ещё раз")
                return 2
        else:
            update.message.reply_text(
                "Введены неправильные данные, проверьте пароль и введите ещё раз")
            return 2


def start(update, context):
    user_id = update.message.from_user.id
    res = get(f"http://localhost:5000/api/users/{user_id}").json()
    if res["message"] == 'ok':
        update.message.reply_text(
            "У вас уже есть аккаунт, \n"
            "для продолжения авторизуйтесь", reply_keyboard=ReplyKeyboardMarkup([], one_time_keyboard=True))
        if user_id not in sessionStorage.keys():
            sessionStorage[user_id] = {
                'login_stage': 0,
                'conv_stage': 0
            }
        return login(update, context)
    else:
        update.message.reply_text(
            "Здравствуйте, это бот "
            "для изучения английского языка, \n"
            "для начала вам нужно зарегистрироваться", reply_keyboard=ReplyKeyboardMarkup([], one_time_keyboard=True))
        return register(update, context)


def learning(update, context):
    user_id = update.message.from_user.id
    update.message.reply_text("Вы в личном кабинете,"
                              "\nЧтобы узнать все команды наберите /help")
    sessionStorage[user_id]['conv_stage'] = 3
    return 3


def logout(update, context):
    update.message.reply_text("Вы вышли из аккаунта, чтобы начать работу выполните команду /start")
    return ConversationHandler.END


def learning_help(update, context):
    from data.commands import commands
    text = """"""
    for com in commands['learning_menu']:
        text += com + '\n'
    update.message.reply_text(text)
    return 3


def get_other_links(update, context):
    from data.english_data import other_links
    user_id = update.message.from_user.id
    mes = update.message.text.strip()
    if mes == 'назад':
        sessionStorage[user_id]['get_links_stage'] = 0
        return learning(update, context)
    if 'get_links_stage' not in sessionStorage[user_id].keys():
        sessionStorage[user_id]['get_links_stage'] = 0
    titles_mes = "Что вы хотите посмотреть? (введите строго нужный текст) " \
                 "\nЧтобы завершить просмотр ссылок введите 'назад'"
    if sessionStorage[user_id]['get_links_stage'] == 0:
        for link in other_links:
            titles_mes += "\n" + link['title']
        sessionStorage[user_id]['get_links_stage'] = 1
        update.message.reply_text(titles_mes, reply_markup=other_links_markup)
        return 4
    else:
        for link in other_links:
            if link['title'] == mes:
                update.message.reply_text(f"""Вот ваш запрос на {link['title']}: 
                                            \n{link['url']}
                                            \nВведите ещё одну тему или напишите 'назад' для выхода в личный кабинет""",
                                          reply_markup=other_links_markup)
                return 4
    update.message("Пожалуйста введите правильные данные!")
    return 4


def get_people_to_chat(update, context):
    res = get("http://localhost:5000/api/users").json()
    text = "Вот люди, с которыми с ты можешь пообщаться." \
           "\nНайди их по никнейму, добавив в начало поиска '@'"
    leng = len(res['users'])
    for user in res['users']:
        if user['id'] == update.message.from_user.id:
            leng -= 1
            continue
        if user['telegram_name'] is None or len(user['telegram_name']) == 0:
            leng -= 1
    if leng > 0:
        cnt = 1
        for i in range(leng):
            if res['users'][i]['id'] != update.message.from_user.id and len(res['users'][i]['telegram_name']):
                text += '\n' + str(cnt) + '. ' + res['users'][i]['telegram_name']
                cnt += 1
    else:
        text = "Извините, но пока у вас нет людей для переписки, \n" \
               "скорее всего у них нет никнейма, поэтому бот не может их найти"
    update.message.reply_text(text)


def get_section_info(update, context):
    from data.english_data import WORDS_FOR_LEARNING
    user_id = update.message.from_user.id
    curr_section = 1
    text = "Вот информация о разделах, которые вы изучаете." \
           "\nВы можете изменить свои цели изучения в личном кабинете."
    aim = sessionStorage[user_id]['user_data']['aim'].split(',')
    for section in aim:
        text += f"\n{curr_section}. {section[0].upper()}{section[1:]}." \
            f"\n\nНемного предисловия к разделу:" \
            f"\n{WORDS_FOR_LEARNING[section]['inception']}" \
            f"\n\nВот обобщение о разделе: " \
            f"\n{WORDS_FOR_LEARNING[section]['conclusion']}"
        curr_section += 1
        text += '\n'
    text += '\nПолностью прочитайте выше сказанное, вы больше не увидите эту информацию'
    text = text.strip()
    update.message.reply_text(text)


def get_lesson(update, context):
    user_id = update.message.from_user.id
    mes = update.message.text.strip()

    from data.english_data import WORDS_FOR_LEARNING
    if 'lesson_stage' not in sessionStorage[user_id].keys():
        sessionStorage[user_id]['lesson_stage'] = 0
        sessionStorage[user_id]['test_stage'] = -1
        sessionStorage[user_id]['section_info_checked'] = 0
        sessionStorage[user_id]['user_data'] = get(f"http://localhost:5000/api/users/{user_id}").json()['user_data']
        if sessionStorage[user_id]['user_data']['aim'][-1] == ',':
            sessionStorage[user_id]['user_data']['aim'] = sessionStorage[user_id]['user_data']['aim'][:-1]

    aim = sessionStorage[user_id]['user_data']['aim'].split(',')
    if sessionStorage[user_id]['lesson_stage'] == 0:
        update.message.reply_text("Вы зашли в раздел занятий."
                                  "\nЗдесь отключены некоторые функции, ведь они будут только отвлекать вас"
                                  "\nТакже можете написать /help_in_lesson, чтобы узнать все команды")
        # показать все темы, предоставить выбор
        if sessionStorage[user_id]['section_info_checked'] == 0:
            get_section_info(update, context)
            sessionStorage[user_id]['section_info_checked'] = 1
        get_all_themes(update, context)
        update.message.reply_text("Чтобы увидеть информацию по какой-либо теме, напишите её.(строго как в сообщении)"
                                  "\nВы также можете написать 'назад' для возвращения в личный кабинет",
                                  reply_markup=themes_markup)
        sessionStorage[user_id]['lesson_stage'] += 1
    elif sessionStorage[user_id]['lesson_stage'] == 1:
        if mes.lower() == 'начать тест':
            update.message.reply_text("Сейчас мы зададим вам несколько вопросов,"
                                      " а вы будете на них отвечать")
            sessionStorage[user_id]['test'] = get_test(user_id)
            sessionStorage[user_id]['anss_given'] = []
            update.message.reply_text(sessionStorage[user_id]['test'][0][0])
            sessionStorage[user_id]['test_stage'] = 1
            sessionStorage[user_id]['conv_stage'] = 5
            return 5
        if sessionStorage[user_id]['test_stage'] != -1:
            if sessionStorage[user_id]['test_stage'] == len(sessionStorage[user_id]['test']):
                sessionStorage[user_id]['anss_given'].append(mes.lower().strip())
                sessionStorage[user_id]['test_stage'] += 1
                text = f"Вот результаты теста: \n"
                score = 0
                test = sessionStorage[user_id]['test']
                for ans_id in range(len(sessionStorage[user_id]['anss_given'])):
                    ans = sessionStorage[user_id]['anss_given'][ans_id].lower().strip()
                    text += '\n' + str(ans_id + 1) + '. ' + test[ans_id][0]
                    text += f"\nВаш ответ: {ans}"
                    if ans == test[ans_id][1].lower().strip():
                        text += '\nПравильно ✓'
                        score += 1
                    else:
                        text += '\nНеправильно ❌'
                        text += f"\nВот правильный ответ: {test[ans_id][1]}"
                text = f"Тест закончен, ваш результат: {str(score)} из" \
                           f" {len(sessionStorage[user_id]['anss_given'])}\n" + text
                update.message.reply_text(text)
                sessionStorage[user_id]['test_stage'] = -1
                update.message.reply_text("Введите 'начать тест', чтобы пройти ещё один тест"
                                          "\nВведите название любой темы, из выше перечисленных,"
                                          " чтобы увидеть её содержание и продолжить обучение"
                                          "\nВведите 'назад', чтобы попасть в личный кабинет",
                                          reply_markup=themes_markup_beg_test)
                return 5
            update.message.reply_text(sessionStorage[user_id]['test'][sessionStorage[user_id]['test_stage']][0])
            sessionStorage[user_id]['anss_given'].append(mes.lower().strip())
            sessionStorage[user_id]['test_stage'] += 1
            sessionStorage[user_id]['conv_stage'] = 5
            return 5
        if mes.lower() == 'назад':
            sessionStorage[user_id]['lesson_stage'] = 0
            sessionStorage[user_id]['test_stage'] = -1
            sessionStorage[user_id]['section_info_checked'] = 0
            sessionStorage[user_id]['user_data'] = get(f"http://localhost:5000/api/users/{user_id}").json()['user_data']
            if sessionStorage[user_id]['user_data']['aim'][-1] == ',':
                sessionStorage[user_id]['user_data']['aim'] = sessionStorage[user_id]['user_data']['aim'][:-1]

            return learning(update, context)

        sections = aim
        lesson = None
        curr_section = None
        for section in sections:
            if lesson is not None:
                break
            for les in WORDS_FOR_LEARNING[section]['themes']:
                if les['title'] == mes:
                    lesson = les
                    curr_section = section
                    sessionStorage[user_id]['curr_section'] = curr_section
                    sessionStorage[user_id]['curr_lesson'] = lesson
                    break
        if lesson is None:
            update.message.reply_text("Введите существующую тему!")
            get_all_themes(update, context)
            update.message.reply_text(reply_markup=themes_markup_beg_test)
            return 5
        lesson_text = f"Вот ваш урок. " \
            f"\n1. Оглавление: {lesson['title']}"
        if len(lesson['youtube_urls']) != 0:
            mnozh = 'a'
            if len(lesson['youtube_urls']) > 1:
                mnozh = 'и'
            lesson_text += f"\n\nВот ссылк{mnozh} на видео по данной тематике:"
            for url in lesson['youtube_urls']:
                lesson_text += f"\n{url}"
        if len(lesson['words']):
            lesson_text += "\n\nВот слова по теме:"
            for word in lesson['words']:
                lesson_text += f'\n{word[0]} - {word[1]}'
        if len(lesson['exsamples']):
            lesson_text += "\n\nВот примеры, где используются слова из темы в контексте:"
            for exsample in lesson['exsamples']:
                lesson_text += f'\n{exsample[0]} -> \n{exsample[1]}'
        if len(lesson['description']):
            lesson_text += f"\n\nДополнительная информация:" \
                f"\n{lesson['description']}"
        lesson_text += '\n\nНе пугайтесь большого объёма информации, потратьте столько времени,' \
                       ' сколько нужно, чтобы овладеть темой.' \
                       "\n\nВведите 'назад', чтобы вернуть в личный кабинет" \
                       "\nВведите 'начать тест', чтобы начать тестирование по словам этой темы" \
                       '\nНапишите название любой темы их предложенных, чтобы увидеть информацию о ней'
        update.message.reply_text(lesson_text, themes_markup_beg_test)
    sessionStorage[user_id]['conv_stage'] = 5
    return 5


def get_all_themes(update, context):
    from data.english_data import WORDS_FOR_LEARNING
    user_id = update.message.from_user.id
    text = "Вот темы, любую из которых вы можете выбрать и изучить или сделать по ним тест:"
    sections = sessionStorage[user_id]['user_data']['aim'].split(',')
    c = 1
    for section in sections:
        cnt = 1
        text += f"\n{str(c)}. {section.title()}"
        for lesson in WORDS_FOR_LEARNING[section]['themes']:
            text += f"\n\t{str(c)}.{str(cnt)} {lesson['title']}"
            cnt += 1
        c += 1
    text = text.strip()
    update.message.reply_text(text)


def help_in_lesson(update, context):
    from data.commands import commands
    text = """"""
    for com in commands['lesson_menu']:
        text += com + '\n'
    update.message.reply_text(text)
    return 5


def change_aim(update, context):
    user_id = update.message.from_user.id
    mes = update.message.text.strip().lower()
    from data.english_data import WORDS_FOR_LEARNING
    user_data = get(f"http://localhost:5000/api/users/{user_id}").json()['user_data']
    if 'change_aim_stage' not in sessionStorage[user_id].keys():
        sessionStorage[user_id]['change_aim_stage'] = 0
    if sessionStorage[user_id]['change_aim_stage'] == 0:
        text = f'Выберите цели изучения английского\n(путешествия, для работы за границей, разговорный),' \
            f'\nесли их несколько, то вводите через запятую(,)'
        update.message.reply_text(text, reply_markup=aims_markup)
        sessionStorage[user_id]['change_aim_stage'] += 1
        return 6
    else:
        sections = ""
        for section in mes.lower().strip().split(','):
            section = section.lower().strip()
            if len(section) == 0:
                continue
            if section not in ['путешествия', 'для работы за границей', 'разговорный']:
                update.message.reply_text(
                    "Выберите цели из предложенных! (путешествия, для работы за границей, разговорный)."
                    "\nЕсли целей много, то вводите их через пробел")
                return 6
            else:
                sections += section + ','
        sections = sections[:-1]
        deliting = delete(f"http://localhost:5000/api/users/{user_id}").json()
        print(deliting)
        res = post('http://localhost:5000/api/users', json={
            'id': user_id,
            'name': user_data['name'],
            'surname': user_data['surname'],
            'email': user_data['email'],
            'password': user_data['password'],
            'address': user_data['address'],
            'age': user_data['age'],
            'aim': sections,
            'telegram_name': update.message.from_user.username,
        }).json()
        print(res)
        update.message.reply_text("Ваши разделы изучения успешно обновлёны!")
        if 'lesson_stage' in sessionStorage[user_id].keys():
            sessionStorage[user_id]['lesson_stage'] = 0
        return learning(update, context)


def talk_to_alice(update, context):
    mes = update.message.text.strip()
    if mes.lower() == 'назад':
        return learning(update, context)
    update.message.reply_text("тип я поговорил, PTK привет")
    return learning(update, context)


def get_test(user_id):
    from data.english_data import WORDS_FOR_LEARNING
    section = sessionStorage[user_id]['curr_section']
    theme = sessionStorage[user_id]['curr_lesson']['title']
    words = []
    for les in WORDS_FOR_LEARNING[section]['themes']:
        if les['title'] == theme:
            words = les['words']
            break
    sam = random.sample(words, k=min(len(words), random.randint(5, 10)))
    test = []
    for i in range(len(sam)):
        en, ru = sam[i]
        q = random.randint(0, 1)
        if q:
            test.append([en + '\n' + "Как сказать это на русском?", ru])
        else:
            test.append([ru + '\n' + "Как сказать это на английском?", en])
    return test


def get_myeng_map(update, context):
    users = get(f"http://localhost:5000/api/users").json()['users']
    marks = ""
    for user in users:
        request = f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode" \
            f"={user['address']}&format=json"
        response = requests.get(request)
        if not response:
            continue
        else:
            json_response = response.json()
            if len(json_response["response"]["GeoObjectCollection"][
                       "featureMember"]) == 0:
                continue
            toponym = \
                json_response["response"]["GeoObjectCollection"][
                    "featureMember"][
                    0]["GeoObject"]
            toponym_coodrinates = toponym["Point"]["pos"]
            longitude, latitude = toponym_coodrinates.split()
            metka = f'{longitude},{latitude},pm'
            metka += 'wt'
            metka += 's' + '~'
            marks += metka
    Zend = ""
    if len(users) == 1:
        Zend = "&z=2"
    static_api_request = f"http://static-maps.yandex.ru/1.x/?" \
                             f"l=map&apikey=40d1649f-0493-4b70-98ba-98533de7710b&pt={marks[:-1]}" + Zend
    context.bot.send_photo(
        update.message.chat_id,  # Идентификатор чата. Куда посылать картинку.
        # Ссылка на static API, по сути, ссылка на картинку.
        # Телеграму можно передать прямо её, не скачивая предварительно карту.
        static_api_request,
        caption=f"Вот пользователи телеграм бота MyEng на карте!"
    )


def stop_translating(update, context):
    user_id = update.message.from_user.id
    if sessionStorage[user_id]['conv_stage'] == 3:
        return learning(update, context)
    else:
        update.message.reply_text("Вы снова в разделе занятий")
        return 5


def switch_to_from_en_to_ru(update, context):
    update.message.reply_text("Введите что нибудь для перевода c английского на русский",
                              reply_markup=ReplyKeyboardMarkup([['назад']], one_time_keyboard=True))
    return 9


def switch_to_from_ru_to_en(update, context):
    update.message.reply_text("Введите что нибудь для перевода с русского на английский",
                              reply_markup=ReplyKeyboardMarkup([['назад']], one_time_keyboard=True))
    return 8


def from_en_to_ru(update, context):
    eng_text = update.message.text.strip()
    if eng_text == 'назад':
        return stop_translating(update, context)
    token = "trnsl.1.1.20200402T145548Z.67d1c0ace063d508.c80570c74bd2edadb651ce9a4fea5da1190d2ee7"
    url_trans = 'https://translate.yandex.net/api/v1.5/tr.json/translate'
    trans_option = {'key': token, 'lang': 'en-ru', 'text': eng_text}
    webRequest = requests.get(url_trans, params=trans_option)
    response = eval(webRequest.text)
    update.message.reply_text(
        "Вот ваш перевод: \n" + response['text'][0] + ""
                                                      "\nЧтобы вернуться в личный кабинет напишите 'назад' "
                                                      "\nИначе, напишете что-нибудь для перевода на русский",
        reply_markup=ReplyKeyboardMarkup([['назад']], one_time_keyboard=True))


def return_to_cabinet(update, context):
    return learning(update, context)


def from_ru_to_en(update, context):
    ru_text = update.message.text.strip()
    if ru_text == 'назад':
        return stop_translating(update, context)
    token = "trnsl.1.1.20200402T145548Z.67d1c0ace063d508.c80570c74bd2edadb651ce9a4fea5da1190d2ee7"
    url_trans = 'https://translate.yandex.net/api/v1.5/tr.json/translate'
    trans_option = {'key': token, 'lang': 'ru-en', 'text': ru_text}
    webRequest = requests.get(url_trans, params=trans_option)
    response = eval(webRequest.text)
    update.message.reply_text(
        "Вот ваш перевод: \n" + response['text'][0] + "\nЧтобы вернуться в личный кабинет напишите 'назад'"
                                                      "\nИначе, введите что-нибудь для перевода с русского на английский"
        , reply_markup=ReplyKeyboardMarkup([['назад']], one_time_keyboard=True))


def run_test(update, context):
    user_id = update.message.from_user.id
    mes = update.message.text.strip()
    if mes.lower() == 'назад':
        sessionStorage[user_id]['test_stage'] = -1
        sessionStorage[user_id]['section_info_checked'] = 0
        sessionStorage[user_id]['user_data'] = get(f"http://localhost:5000/api/users/{user_id}").json()[
            'user_data']
        if sessionStorage[user_id]['user_data']['aim'][-1] == ',':
            sessionStorage[user_id]['user_data']['aim'] = sessionStorage[user_id]['user_data']['aim'][:-1]
        return learning(update, context)
    if mes.lower() == 'завершить тест':
        sessionStorage[user_id]['test_stage'] += 1
        text = f"Вот результаты теста: \n"
        score = 0
        test = sessionStorage[user_id]['test']
        for ans_id in range(len(sessionStorage[user_id]['anss_given'])):
            ans = sessionStorage[user_id]['anss_given'][ans_id].lower().strip()
            text += '\n' + str(ans_id + 1) + '. ' + test[ans_id][0]
            text += f"\nВаш ответ: {ans}"
            if ans == test[ans_id][1].lower().strip():
                text += '\nПравильно ✓'
                score += 1
            else:
                text += '\nНеправильно ❌'
                text += f"\nВот правильный ответ: {test[ans_id][1]}"
        text = f"Тест закончен, ваш результат: {str(score)} из" \
                   f" {len(sessionStorage[user_id]['anss_given'])}\n" + text
        update.message.reply_text(text)
        sessionStorage[user_id]['test_stage'] = -1
        update.message.reply_text("Введите 'начать тест', чтобы пройти ещё один тест"
                                  "\nВведите 'назад' для перехода в личный кабинет",
                                  reply_markup=ReplyKeyboardMarkup([['начать тест'], ['назад']],
                                                                   one_time_keyboard=True))
        return 10
    if 'test_stage' not in sessionStorage[user_id].keys():
        sessionStorage[user_id]['test_stage'] = -1
        sessionStorage[user_id]['user_data'] = get(f"http://localhost:5000/api/users/{user_id}").json()['user_data']
        if sessionStorage[user_id]['user_data']['aim'][-1] == ',':
            sessionStorage[user_id]['user_data']['aim'] = sessionStorage[user_id]['user_data']['aim'][:-1]

    aim = sessionStorage[user_id]['user_data']['aim'].split(',')
    if sessionStorage[user_id]['test_stage'] == -1:
        # показать все темы, предоставить выбор
        get_all_themes(update, context)
        update.message.reply_text("Чтобы начать тест по какой-либо теме, напишите её."
                                  "\n(строго как в сообщении)"
                                  "\nВы также можете написать 'назад' для возвращения в личный кабинет",
                                  reply_markup=themes_markup)
        sessionStorage[user_id]['anss_given'] = []
        sessionStorage[user_id]['test_stage'] += 1

        return 10
    elif sessionStorage[user_id]['test_stage'] == 0:
        from data.english_data import WORDS_FOR_LEARNING
        theme = mes.strip()
        found = 0
        sessionStorage[user_id]['curr_lesson'] = None
        for section in aim:
            if found:
                break
            for lesson in WORDS_FOR_LEARNING[section]['themes']:
                if lesson['title'] == theme:
                    sessionStorage[user_id]['curr_section'] = section
                    sessionStorage[user_id]['curr_lesson'] = lesson
                    found = 1
                    break
        if sessionStorage[user_id]['curr_lesson'] is None:
            update.message.reply_text("Введите пожалуйста существующую тему!", reply_markup=themes_markup)
            return 10
        if sessionStorage[user_id]['curr_section'] == 'разговорный':
            update.message.reply_text("Это тема раздела 'разговоный',"
                                      " поэтому здесь нет слов для теста", reply_markup=themes_markup_beg_test)
            return 10
        update.message.reply_text("Сейчас мы зададим вам несколько вопросов,"
                                  " а вы будете на них отвечать")
        sessionStorage[user_id]['test'] = get_test(user_id)
        sessionStorage[user_id]['anss_given'] = []
        update.message.reply_text(sessionStorage[user_id]['test'][0][0],
                                  reply_markup=ReplyKeyboardMarkup([['завершить тест']], one_time_keyboard=True))
        sessionStorage[user_id]['test_stage'] = 1
        return 10
    else:
        if sessionStorage[user_id]['test_stage'] == len(sessionStorage[user_id]['test']):
            sessionStorage[user_id]['anss_given'].append(mes.lower().strip())
            sessionStorage[user_id]['test_stage'] += 1
            text = f"Вот результаты теста: \n"
            score = 0
            test = sessionStorage[user_id]['test']
            for ans_id in range(len(sessionStorage[user_id]['anss_given'])):
                ans = sessionStorage[user_id]['anss_given'][ans_id].lower().strip()
                text += '\n' + str(ans_id + 1) + '. ' + test[ans_id][0]
                text += f"\nВаш ответ: {ans}"
                if ans == test[ans_id][1].lower().strip():
                    text += '\nПравильно ✓'
                    score += 1
                else:
                    text += '\nНеправильно ❌'
                    text += f"\nВот правильный ответ: {test[ans_id][1]}"
            text = f"Тест закончен, ваш результат: {str(score)} из" \
                       f" {len(sessionStorage[user_id]['anss_given'])}\n" + text
            update.message.reply_text(text)
            sessionStorage[user_id]['test_stage'] = -1
            update.message.reply_text("Введите 'начать тест', чтобы пройти ещё один тест"
                                      "\nВведите 'назад' для перехода в личный кабинет",
                                      reply_markup=ReplyKeyboardMarkup([['начать тест'], ['назад']],
                                                                       one_time_keyboard=True))
            return 10
        else:
            update.message.reply_text(sessionStorage[user_id]['test'][sessionStorage[user_id]['test_stage']][0],
                                  reply_markup=ReplyKeyboardMarkup([['завершить тест']], one_time_keyboard=True))
            sessionStorage[user_id]['anss_given'].append(mes.lower().strip())
            sessionStorage[user_id]['test_stage'] += 1
            return 10


def stop_test(update, context):
    user_id = update.message.from_user.id
    text = f"Вот результаты теста: \n"
    score = 0
    test = sessionStorage[user_id]['test']
    for ans_id in range(len(sessionStorage[user_id]['anss_given'])):
        ans = sessionStorage[user_id]['anss_given'][ans_id].lower().strip()
        text += '\n' + str(ans_id + 1) + '. ' + test[ans_id][0]
        text += f"\nВаш ответ: {ans}"
        if ans == test[ans_id][1].lower().strip():
            text += '\nПравильно ✓'
            score += 1
        else:
            text += '\nНеправильно ❌'
            text += f"\nВот правильный ответ: {test[ans_id][1]}"
    text = f"Тест закончен, ваш результат: {str(score)} из" \
               f" {len(sessionStorage[user_id]['anss_given'])}\n" + text
    update.message.reply_text(text)
    sessionStorage[user_id]['test_stage'] = -1
    update.message.reply_text("Введите 'начать тест', чтобы пройти ещё один тест"
                              "\nВведите название любой темы, из выше перечисленных,"
                              " чтобы увидеть её содержание и продолжить обучение"
                              "\nВведите 'назад' для перехода в личный кабинет"
                              "\nВведите 'завершить тест', что бы досрочно завершить тест",
                              reply_markup=themes_markup_beg_test)
    return 10


def unauthed(update, context):
    update.message.reply_text("Вы не авторизованы, чтобы начать работу выполните команду /start")


if __name__ == "__main__":
    db_session.global_init("db/baza.db")
    REQUEST_KWARGS = {
        'proxy_url': 'socks5://localhost:9150',  # Адрес прокси сервера
    }
    updater = Updater(TOKEN_FOR_TELEGRAM_BOT, use_context=True, request_kwargs=REQUEST_KWARGS)
    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        fallbacks=[CommandHandler('logout', logout)],
        states={
            # регистрация
            1: [MessageHandler(Filters.text, register)],
            # авторизация
            2: [MessageHandler(Filters.text, login)],
            # пользователь в MYENG
            3: [CommandHandler("logout", logout),
                CommandHandler("get_other_links", get_other_links),
                CommandHandler("get_people_to_chat", get_people_to_chat),
                CommandHandler("get_myeng_map", get_myeng_map),
                CommandHandler("help", learning_help),
                CommandHandler("get_lesson", get_lesson),
                CommandHandler("change_aim", change_aim),
                CommandHandler("FromEngToRUS", switch_to_from_en_to_ru),
                CommandHandler("FromRusToEng", switch_to_from_ru_to_en),
                CommandHandler("run_test", run_test),
                MessageHandler(Filters.text, learning)],
            4: [MessageHandler(Filters.text, get_other_links)],  # other links
            5: [CommandHandler("get_people_to_chat", get_people_to_chat),
                CommandHandler('help_in_lesson', help_in_lesson),
                CommandHandler("return_to_cabinet", return_to_cabinet),
                MessageHandler(Filters.text, get_lesson)],  # lesson
            6: [MessageHandler(Filters.text, change_aim)],  # aim changing
            7: [MessageHandler(Filters.text, talk_to_alice)],  # dialog with Alice
            8: [CommandHandler("FromEngToRUS", switch_to_from_en_to_ru),
                CommandHandler("FromRusToEng", switch_to_from_ru_to_en),
                MessageHandler(Filters.text, from_ru_to_en)],
            9: [CommandHandler("FromEngToRUS", switch_to_from_en_to_ru),
                CommandHandler("FromRusToEng", switch_to_from_ru_to_en),
                MessageHandler(Filters.text, from_en_to_ru)],
            10: [MessageHandler(Filters.text, run_test), CommandHandler("stop_test", stop_test)]
        }
    )
    dp.add_handler(conv_handler)
    dp.add_handler(MessageHandler(Filters.text, unauthed))
    updater.start_polling()
    updater.idle()
