"""MyEng - Телеграм бот для узучения английского языка"""
import datetime
from flask import Flask, render_template, jsonify
import datetime
from flask import Flask, render_template, request
from flask_login import LoginManager, login_user, logout_user, \
    login_required
from flask_restful import Resource, Api, reqparse
from flask_wtf import FlaskForm
from requests import post, get, delete
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
                "\nЕсли целей много, то вводите их через пробел")
            return 1
        else:
            sessionStorage[user_id]["reg_form"].aim += section + ','
    sessionStorage[user_id]["reg_form"].aim = sessionStorage[user_id]["reg_form"].aim[::-1]
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
                'login_stage': 0
            }
        return login(update, context)
    else:
        update.message.reply_text(
            "Здравствуйте, это бот "
            "для изучения английского языка, \n"
            "для начала вам нужно зарегистрироваться")
        return register(update, context)


def learning(update, context):
    update.message.reply_text("Вы снова в личном кабинете,"
                              "\nЧтобы узнать все команды наберите /help")
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
                 "\nЧтобы завершить просмотр ссылок введите 'стоn'"
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
                                            \n{link['url']}""")
                return 4
    update.message("Пожалуйста введите правильные данные!")
    return 4


def get_people_to_chat(update, context):
    update.message.reply_text("Вот люди, с которыми с ты можешь пообщаться"
                              "\n(не удивляетесь своему имени),"
                              "\nнайди их по никнейму, добавив в начало поиска '@'")
    res = get("http://localhost:5000/api/users").json()
    text = ""
    for i in range(len(res['users'])):
        if res['users'][i].id != update.message.from_user.id:
            text += str(i + 1) + '. ' + res['users'][i]['telegram_name']
    update.message.reply_text(text)
    return 3


def recs_for_speakers(update, context):
    update.message.reply_text("""1. Медленного темпа речи
                                Нет ничего страшного в том, что вы говорите не так быстро, как иностранцы,
                                делаете паузы или подбираете слова. Для вас общение на английском — нечто новое,
                                к чему нужно привыкнуть. Зато если вы будете стараться чаще говорить с людими,
                                которые знают английский, то вы значительно пошатнёте пресловутый языковой барьер.
                                \n2. Грамматических ошибок
                                Вы находитесь не на экзамене, поэтому не бойтесь ошибаться.
                                Люди, которые знают английский, все равно поймут вас,
                                даже если вы случайно пропустите вспомогательный глагол или употребите не то время.
                                Все прекрасно понимают, что английский язык для вас не является родным,
                                поэтому не будут обращать внимания на небольшие погрешности.
                                \n3. Лексических ошибок
                                Некоторые люди боятся запутаться в английской лексике.
                                Мы советуем ознакомиться со статьей: «Miscommunication abroad или как я ела мыло на обед».
                                Вы увидите, нет ничего страшного в путанице, всегда можно найти выход из положения и
                                объяснить другими словами, что вам нужно.
                                \n4. Акцента
                                Наш последний совет: сохраняйте спокойствие и имитируйте британский акцент.
                                Во многих из нас живет страх: я не смогу говорить как настоящий англичанин или американец,
                                у меня акцент, это может звучать смешно. Совершенно необоснованная фобия.
                                Во-первых, у каждого человека есть свои собственные особенности речи, интонации, произношения. 
                                Во-вторых, в любой стране есть местный вариант английского: в некоторых языках нет звука «ш»,
                                в каком-то отсутствует «ч», кому-то сложно научиться произносить сочетание th — так и
                                формируются разные акценты в английском жителей различных стран.
                                Тем не менее, это не мешает миллионам людей изучать язык, общаться и понимать друг друга.
                                Кстати, многие считают, что австралийский и канадский английский звучат еще более экзотично,
                                чем наша с вами речь.""")


def get_section_info(update, context):
    from data.english_data import WORDS_FOR_LEARNING
    user_id = update.message.from_user.id
    curr_section = 1
    text = "Вот информация о разделах, которые вы изучаете." \
           "\nВы можете изменить свои цели изучения в личном кабинете."
    aim = sessionStorage[user_id]['user_data']['aim']
    for section in aim.split(','):
        text += f"{curr_section} {section.title()}." \
                f"\nНемного предисловия к разделу:" \
                f"\n{WORDS_FOR_LEARNING[section]['inception']}" \
                f"\nВот обобщение о разделе: " \
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
        sessionStorage[user_id]['user_data'] = get(f"http://localhost:5000/api/users/{user_id}").json()['user_data']

    aim = sessionStorage[user_id]['user_data']['aim'].split(',')
    if sessionStorage[user_id]['lesson_stage'] == 0:
        # показать все темы, предоставить выбор
        get_section_info(update, context)
        get_all_themes()
        chose_one_of_them()
        get_either_test_either_some_other_game_of_words()
    return 3


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
            update.message.reply_text("Ваша раздел изучения успешно обновлён!")
            if 'lesson_stage' in sessionStorage[user_id].keys():
                sessionStorage[user_id]['lesson_stage'] = 0
            return learning(update, context)


def talk_to_alice(update, context):
    mes = update.message.text.strip()
    if mes.lower() == 'стоп':
        return learning(update, context)
    update.message.reply_text("тип я поговорил, PTK привет")
    return learning(update, context)


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
                CommandHandler("help", learning_help),
                CommandHandler("get_lesson", get_lesson),
                CommandHandler("change_aim", change_aim),
                MessageHandler(Filters.text, learning)],
            4: [MessageHandler(Filters.text, get_other_links)],  # other links
            5: [MessageHandler(Filters.text, get_lesson),
                CommandHandler('help_in_lesson', help_in_lesson)],  # lesson
            6: [MessageHandler(Filters.text, change_aim)],  # aim changing
            7: [MessageHandler(Filters.text, talk_to_alice)]  # dialog with Alice
        }
    )
    dp.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()
