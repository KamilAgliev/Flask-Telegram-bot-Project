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
    mes = update.message.text
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
    if mes not in ['путешествия', 'для работы за границей', 'разговорный']:
        update.message.reply_text(
            "Выберите одно из предложенных направлений! (путешествия, для работы за границей, разговорный)")
        return 1
    sessionStorage[user_id]["reg_form"].aim = mes
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
    mes = update.message.text
    user_id = update.message.from_user.id
    if sessionStorage[user_id]['login_stage'] == 0:
        update.message.reply_text("Введите email и пароль от вашего аккаунта через пробел")
        sessionStorage[user_id]['login_stage'] += 1
        return 2
    else:
        given_email, given_password = mes.split()
        res = get(f"http://localhost:5000/api/users/{user_id}").json()
        if res['message'] == "ok":
            ses = db_session.create_session()
            user = ses.query(User).filter(User.id == user_id).first()
            if user and user.check_password(given_password):
                sessionStorage[user_id]['login_stage'] = 0
                return learning(update, context)
            else:
                update.message.reply_text(
                    "Введены неправильные данные, \n скорее всего ошибка в пароле, \n введите данные ещё раз")
                return 2
        else:
            update.message.reply_text(
                "Введены неправильные данные, \n проверьте логин и пароль, \n и введите ещё раз")
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
    mes = update.message.text
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


def get_lesson(update, context):
    user_id = update.message.from_user.id
    mes = update.message.text

    if 'lesson_stage' not in sessionStorage[user_id].keys():
        sessionStorage[user_id]['lesson_stage'] = 0
        sessionStorage[user_id]['user_data'] = get(f"http://localhost:5000/api/users/{user_id}").json()['user_data']
    if sessionStorage[user_id]['lesson_stage'] == 0:
        update.message.reply_text(
            f"На данный момент вы изучаете этот раздел: {sessionStorage[user_id]['user_data']['aim']}"
            "Чтобы узнать команды введите /help_in_lesson")
        return 5


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
        sessionStorage[user_id]['other_themes'] = {'путешествия': 1, 'для работы за границей': 1, 'разговорный': 1}
        sessionStorage[user_id]['other_themes'][user_data['aim']] = 0
    if sessionStorage[user_id]['change_aim_stage'] == 0:
        if (len(WORDS_FOR_LEARNING[user_data['aim']]['themes']) + 1) // 2 > user_data['curr_lesson']:
            text = "\nВы изучили не так много в этом разделе," \
                   "\nподумайте хорошо перед решением."
        else:
            text = "\nВы уже изучили достаточно в этом разделе," \
                   "\nсамое время перейти в другой!"
            text += '\n'
        a, b = None, None
        for key in sessionStorage[user_id]['other_themes'].keys():
            if sessionStorage[user_id]['other_themes'][key] == 1:
                if a is None:
                    a = key
                else:
                    b = key
        text += f'\nВыберите одно из других направлений \n({a}, {b})'
        update.message.reply_text(text)
        sessionStorage[user_id]['change_aim_stage'] += 1
        return 6
    else:
        if mes not in ['путешествия', 'для работы за границей', 'разговорный']:
            update.message.reply_text("Пожалуйста введите правильые данные"
                                      "\n(путешествия, для работы за границей, разговорный)")
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
            5: [MessageHandler(Filters.text, get_other_links),
                CommandHandler('help_in_lesson', help_in_lesson)],  # lesson
            6: [MessageHandler(Filters.text, change_aim)]
        }
    )
    dp.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()
