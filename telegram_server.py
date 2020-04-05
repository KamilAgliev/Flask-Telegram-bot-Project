"""MyEng - Телеграм бот для узучения английского языка"""
import datetime
from flask import Flask, render_template, jsonify
import datetime
from flask import Flask, render_template, request
from flask_login import LoginManager, login_user, logout_user, \
    login_required
from flask_restful import Resource, Api, reqparse
from flask_wtf import FlaskForm
from requests import post, get
from werkzeug.exceptions import abort
from werkzeug.utils import redirect
from wtforms import PasswordField, BooleanField, SubmitField, StringField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
from flask import make_response

import flask_server
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
    res = get(f"http://127.0.0.1:5000/api/users/{user_id}").json()
    if res["message"] == 'ok':
        update.message.reply_text("У вас уже есть аккаунт!")
        sessionStorage[user_id]["login_stage"] = 0
        return login(update, context)
    else:
        if user_id not in sessionStorage.keys():
            form = RegisterForm()
            sessionStorage[user_id] = {
                'has_account': True,
                "register_stage": 0,
                "reg_form": form,
                "reg_ended": False,
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
    if mes not in ["учитель", "ученик"]:
        update.message.reply_text("Введите либо учитель, либо ученик")
        return 1
    sessionStorage[user_id]["reg_form"].position = mes
    data = sessionStorage[user_id]["reg_form"]
    res = post('http://127.0.0.1:5000/api/users', json={
        'id': user_id,
        'name': data.name,
        'surname': data.surname,
        'email': data.email,
        'password': data.password,
        'address': data.address,
        'age': data.age,
        'position': data.position
    }).json()
    print(res)
    sessionStorage[user_id]["login_stage"] = 0
    sessionStorage[user_id]["reg_ended"] = True
    update.message.reply_text("Вы успешно зарегестрированы!")
    return login(update, context)


def login(update, context):
    mes = update.message.text
    user_id = update.message.from_user.id
    if sessionStorage[user_id]['login_stage'] == 0:
        update.message.reply_text("Введите email и пароль от вашего аккаунта через пробел")
        sessionStorage[user_id]['login_stage'] += 1
        return 2
    else:
        given_email, given_password = mes.split()
        res = get(f"http://127.0.0.1:5000/api/users/{user_id}").json()
        if res['message'] == "ok":
            ses = db_session.create_session()
            user = ses.query(User).filter(User.id == user_id).first()
            if user and user.check_password(given_password):
                sessionStorage[user_id]['auth'] = True
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
    res = get(f"http://127.0.0.1:5000/api/users/{user_id}").json()
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
    update.message.reply_text("Вы успешно зашли в свой аккаунт, \n теперь вы можете использовать весь функционал бота")
    return 3


def logout(update, context):
    user_id = update.message.from_user.id
    update.message.reply_text("Вы вышли из аккаунта, чтобы начать работы выполните команду /start")
    sessionStorage[user_id]['auth'] = False
    return ConversationHandler.END


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
            3: [CommandHandler("logout", logout), MessageHandler(Filters.text, learning)],
        }
    )
    dp.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()
