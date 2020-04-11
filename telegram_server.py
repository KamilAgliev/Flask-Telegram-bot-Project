"""MyEng - Телеграм бот для узучения английского языка"""
import datetime

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

from data.auth import TOKEN_FOR_TELEGRAM_BOT
# Импортируем необходимые классы.
from telegram.ext import Updater, MessageHandler, Filters, ConversationHandler
from telegram.ext import CallbackContext, CommandHandler
from data.auth import sessionStorage


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
        if section not in ['путешествия', 'для работы за границей', 'разговорный']:
            update.message.reply_text(
                "Выберите цели из предложенных! (путешествия, для работы за границей, разговорный)."
                "\nЕсли целей много, то вводите их через запятую(,)")
            return 1
        else:
            sessionStorage[user_id]["reg_form"].aim += section + ','
    sessionStorage[user_id]['reg_form'].aim = sessionStorage[user_id]['reg_form'].aim[:-1]
    data = sessionStorage[user_id]["reg_form"]
    res = post('http://localhost:5000/api/users', json={
        'id': user_id,
        'name': data.name,
        'surname': data.surname,
        'email': data.email,
        'password': data.password,
        'address': data.address,
        'age': data.age,
        'aim': data.aim,
        'telegram_name': update.message.from_user.username,
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
                    "Введены неправильные данные, скорее всего ошибка в пароле."
                    "\nвведите данные ещё раз")
                return 2
        else:
            update.message.reply_text(
                "Введены неправильные данные, проверьте логин и пароль и введите ещё раз")
            return 2


def start(update, context):
    user_id = update.message.from_user.id
    res = get(f"http://localhost:5000/api/users/{user_id}").json()
    if res["message"] == 'ok':
        update.message.reply_text(
            "Здравствуйте, это бот "
            "для изучения английского языка, \n"
            "для продолжения авторизуйтесь")
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
            "для начала вам нужно зарегистрироваться")
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
    if mes == 'стоп':
        sessionStorage[user_id]['get_links_stage'] = 0
        return learning(update, context)
    if 'get_links_stage' not in sessionStorage[user_id].keys():
        sessionStorage[user_id]['get_links_stage'] = 0
    titles_mes = "Что вы хотите посмотреть? (введите строго нужный текст) " \
                 "\nЧтобы завершить просмотр ссылок введите 'стоп'"
    if sessionStorage[user_id]['get_links_stage'] == 0:
        for link in other_links:
            titles_mes += "\n" + link['title']
        sessionStorage[user_id]['get_links_stage'] = 1
        update.message.reply_text(titles_mes)
        return 4
    else:
        for link in other_links:
            if link['title'] == mes:
                update.message.reply_text(f"""Вот ваш запрос на {link['title']}: 
                                            \n{link['url']}
                                            \nВведите ещё одну тему или напишите 'стоп' для выхода в личный кабинет""")
                return 4
    update.message("Пожалуйста введите правильные данные!")
    return 4


def get_people_to_chat(update, context):
    res = get("http://localhost:5000/api/users").json()
    text = "Вот люди, с которыми с ты можешь пообщаться." \
           "\nНайди их по никнейму, добавив в начало поиска '@'"
    leng = len(res['users'])
    if leng > 1:
        for i in range(leng):
            if res['users'][i]['id'] != update.message.from_user.id:
                text += '\n' + str(i + 1) + '. ' + res['users'][i]['telegram_name']
    else:
        text = "Извините, но пока ботом пользуетесь только вы!"
    update.message.reply_text(text)


def get_section_info(update, context):
    from data.english_data import WORDS_FOR_LEARNING
    user_id = update.message.from_user.id
    curr_section = 1
    text = "Вот информация о разделах, которые вы изучаете." \
           "\nВы можете изменить свои цели изучения в личном кабинете."
    aim = sessionStorage[user_id]['user_data']['aim']
    for section in aim.split(','):
        text += f"\n{curr_section}. {section.title()}." \
            f"\n\nНемного предисловия к разделу:" \
            f"\n{WORDS_FOR_LEARNING[section]['inception']}" \
            f"\n\nВот обобщение о разделе: " \
            f"\n{WORDS_FOR_LEARNING[section]['conclusion']}"
        curr_section += 1
        text += '\n'
    text = text.strip()
    update.message.reply_text(text)


def get_lesson(update, context):
    user_id = update.message.from_user.id
    mes = update.message.text.strip()

    from data.english_data import WORDS_FOR_LEARNING
    if 'lesson_stage' not in sessionStorage[user_id].keys():
        sessionStorage[user_id]['lesson_stage'] = 0
        sessionStorage[user_id]['test_stage'] = -1
        sessionStorage[user_id]['user_data'] = get(f"http://localhost:5000/api/users/{user_id}").json()['user_data']

    aim = sessionStorage[user_id]['user_data']['aim'].split(',')
    if sessionStorage[user_id]['lesson_stage'] == 0:
        update.message.reply_text("Вы зашли в раздел занятий."
                                  "\nЗдесь отключены некоторые функции, ведь они будут только отвлекать вас"
                                  "\nТакже можете написать /help_in_lesson, чтобы узнать все команды")
        # показать все темы, предоставить выбор
        get_section_info(update, context)
        get_all_themes(update, context)
        update.message.reply_text("Чтобы увидеть информацию по какой-либо теме, напишите её.(строго как в сообщении)"
                                  "\nВы также можете написать 'стоп' для возвращения в личный кабинет")
        sessionStorage[user_id]['lesson_stage'] += 1
    elif sessionStorage[user_id]['lesson_stage'] == 1:
        if mes.lower() == 'начать тест':
            sessionStorage[user_id]['test_stage'] = 0
            update.message.reply_text("Сейчас мы зададим вам несколько вопросов,"
                                      " а вы будете на них отвечать")
            sessionStorage[user_id]['test'] = get_test(sessionStorage[user_id]['curr_section'], user_id)
            sessionStorage[user_id]['score'] = 0
            sessionStorage[user_id]['true'] = 0
            sessionStorage[user_id]['false'] = 0
            update.message.reply_text()
            sessionStorage[user_id]['conv_stage'] = 5
            return 5
        if sessionStorage[user_id]['test_stage'] != -1:
            if sessionStorage[user_id]['test_stage'] == len(sessionStorage[user_id]['test']):
                update.message.reply_text(
                    f"Тест закончен, ваш результат: {str(sessionStorage[user_id]['score'])} из"
                    f" {str(len(sessionStorage[user_id]['test']))}"
                    f"Вот правильные овтеты: ")
            update.message.reply_text(sessionStorage[user_id]['test'][sessionStorage[user_id]['test_stage']])
            sessionStorage[user_id]['test_stage'] += 1

            sessionStorage[user_id]['conv_stage'] = 5
            return 5
        if mes.lower() == 'стоп':
            sessionStorage[user_id]['lesson_stage'] = 0
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
            lesson_text += "\nВот примеры, где используются слова из темы в контексте, что очень важно"
            for exsample in lesson['exsamples']:
                lesson_text += f'\n{exsample}'
        if len(lesson['description']):
            lesson_text += f"\nДополнительная информация:" \
                f"\n{lesson['description']}"
        lesson_text += '\n\nНе пугайтесь большого объёма информации, потратьте столько времени,' \
                       ' сколько нужно, чтобы овладеть темой.' \
                       "\nВведите 'стоп', чтобы вернуть в личный кабинет" \
                       "\nВведите 'начать тест', чтобы начать тестирование по словам этой темы" \
                       '\nНапишите название любой темы их предложенных, чтобы увидеть информацию о ней'
        update.message.reply_text(lesson_text)
    sessionStorage[user_id]['conv_stage'] = 5
    return 5


def get_all_themes(update, context):
    from data.english_data import WORDS_FOR_LEARNING
    user_id = update.message.from_user.id
    text = "Вот темы, любую из которых вы можете выбрать и изучить:"
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
    mes = update.message.text
    from data.english_data import WORDS_FOR_LEARNING
    user_data = get(f"http://localhost:5000/api/users/{user_id}").json()['user_data']
    if 'change_aim_stage' not in sessionStorage[user_id].keys():
        sessionStorage[user_id]['change_aim_stage'] = 0
    if sessionStorage[user_id]['change_aim_stage'] == 0:
        text = f'Выберите цели изучения английского(путешествия, для работы за границей, разговорный),' \
            f'\nесли их несколько, то вводите через запятую(,)'
        update.message.reply_text(text)
        sessionStorage[user_id]['change_aim_stage'] += 1
        return 6
    else:
        for section in mes.lower().split(','):
            section = section.lower().strip()
            if section not in ['путешествия', 'для работы за границей', 'разговорный']:
                update.message.reply_text(
                    "Выберите цели из предложенных! (путешествия, для работы за границей, разговорный)."
                    "\nЕсли целей много, то вводите их через пробел")
                return 6
        else:
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
                'aim': mes,
                'telegram_name': update.message.from_user.username,
            }).json()
            print(res)
            update.message.reply_text("Ваши разделы изучения успешно обновлёны!")
            if 'lesson_stage' in sessionStorage[user_id].keys():
                sessionStorage[user_id]['lesson_stage'] = 0
            return learning(update, context)


def talk_to_alice(update, context):
    mes = update.message.text.strip()
    if mes.lower() == 'стоп':
        return learning(update, context)
    update.message.reply_text("тип я поговорил, PTK привет")
    return learning(update, context)


def get_test(theme, user_id):
    from data.english_data import WORDS_FOR_LEARNING
    section = sessionStorage[user_id]['curr_section']
    leng = WORDS_FOR_LEARNING[]


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
    update.message.reply_text("Введите что нибудь для перевода на русский")
    return 10


def switch_to_from_ru_to_en(update, context):
    update.message.reply_text("Введите что нибудь для перевода на английский")
    return 9


def from_en_to_ru(update, context):
    eng_text = update.message.text.strip()
    if eng_text == 'стоп':
        return learning(update, context)
    token = "trnsl.1.1.20200402T145548Z.67d1c0ace063d508.c80570c74bd2edadb651ce9a4fea5da1190d2ee7"
    url_trans = 'https://translate.yandex.net/api/v1.5/tr.json/translate'
    trans_option = {'key': token, 'lang': 'en-ru', 'text': eng_text}
    webRequest = requests.get(url_trans, params=trans_option)
    response = eval(webRequest.text)
    update.message.reply_text(
        "Вот ваш перевод: \n" + response['text'][0] + "\nЧтобы вернуться в личный кабинет напишите 'стоп'")


def from_ru_to_en(update, context):
    ru_text = update.message.text.strip()
    if ru_text == 'стоп':
        return learning(update, context)
    token = "trnsl.1.1.20200402T145548Z.67d1c0ace063d508.c80570c74bd2edadb651ce9a4fea5da1190d2ee7"
    url_trans = 'https://translate.yandex.net/api/v1.5/tr.json/translate'
    trans_option = {'key': token, 'lang': 'ru-en', 'text': ru_text}
    webRequest = requests.get(url_trans, params=trans_option)
    response = eval(webRequest.text)
    update.message.reply_text(
        "Вот ваш перевод: \n" + response['text'][0] + "\nЧтобы вернуться в личный кабинет напишите 'стоп'")


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
                MessageHandler(Filters.text, learning)],
            4: [MessageHandler(Filters.text, get_other_links)],  # other links
            5: [CommandHandler("get_people_to_chat", get_people_to_chat),
                CommandHandler('help_in_lesson', help_in_lesson),
                MessageHandler(Filters.text, get_lesson)],  # lesson
            6: [MessageHandler(Filters.text, change_aim)],  # aim changing
            7: [MessageHandler(Filters.text, talk_to_alice)],  # dialog with Alice
            9: [CommandHandler("FromEngToRUS", switch_to_from_en_to_ru),
                CommandHandler("FromRusToEng", switch_to_from_ru_to_en),
                MessageHandler(Filters.text, from_ru_to_en)],
            10: [CommandHandler("FromEngToRUS", switch_to_from_en_to_ru),
                 CommandHandler("FromRusToEng", switch_to_from_ru_to_en),
                 MessageHandler(Filters.text, from_en_to_ru)],
        }
    )
    dp.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()
