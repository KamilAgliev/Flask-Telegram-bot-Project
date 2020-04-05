"""MyEng - Телеграм бот для узучения английского языка"""
import datetime
from flask import Flask, render_template, jsonify
import datetime
from flask import Flask, render_template, request
from flask_login import LoginManager, login_user, current_user, logout_user, \
    login_required
from flask_restful import Resource, Api, reqparse
from flask_wtf import FlaskForm
from requests import post
from werkzeug.exceptions import abort
from werkzeug.utils import redirect
from wtforms import PasswordField, BooleanField, SubmitField, StringField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
from flask import make_response
from data import db_session
from data.users import User
from flask_server import RegisterForm, logout, log_user
from resources import users_resources

from data.auth import TOKEN_FOR_TELEGRAM_BOT
# Импортируем необходимые классы.
from telegram.ext import Updater, MessageHandler, Filters, ConversationHandler
from telegram.ext import CallbackContext, CommandHandler
from data.auth import sessionStorage


def register(update, context):
    mes = update.message.text
    user_id = update.message.from_user.id
    if user_id in sessionStorage.keys() and sessionStorage[user_id]['has_account'] and sessionStorage[user_id][
        'register_stage'] == 7 and sessionStorage[user_id]["reg_ended"]:
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
    if stage != 7:
        if stage != 0:
            if stage == 1:
                sessionStorage[user_id]["reg_form"].name = mes
            if stage == 2:
                sessionStorage[user_id]["reg_form"].surname = mes
            if stage == 3:
                sessionStorage[user_id]["reg_form"].email = mes
            if stage == 4:
                sessionStorage[user_id]["reg_form"].password = mes
            if stage == 5:
                sessionStorage[user_id]["reg_form"].password_again = mes
            if stage == 6:
                sessionStorage[user_id]["reg_form"].age = int(mes)
        update.message.reply_text(RegisterForm.stages[stage])
        sessionStorage[user_id]['register_stage'] += 1
        return 1
    sessionStorage[user_id]["reg_form"].address = mes
    data = sessionStorage[user_id]["reg_form"]
    res = post('http://127.0.0.1:5000/api/users', json={
        'name': data.name,
        'surname': data.surname,
        'email': data.email,
        'password': data.password,
        'address': data.address,
        'age': data.age
    }).json()
    print(res)
    sessionStorage[user_id]["login_stage"] = 0
    sessionStorage[user_id]["reg_ended"] = True
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
        connect = db_session.create_session()
        user = connect.query(User).filter(User.email == given_email).first()
        if user and user.check_password(given_password):
            log_user(user)
            sessionStorage[user_id]['login_stage'] = 0
            return login(update, context)
        else:
            update.message.reply_text("Введены неправильные данные, попробуйте ещё раз")
            return 2


def start(update, context):
    user_id = update.message.from_user.id
    if user_id not in sessionStorage.keys():
        update.message.reply_text(
            "Здравствуйте, это бот "
            "для изучения английского языка, \n"
            "для начала вам нужно зарегистрироваться")
        return register(update, context)
    else:
        update.message.reply_text(
            "Здравствуйте, это бот "
            "для изучения английского языка, \n"
            "для продолжения авторизуйтесь")
        sessionStorage[user_id]['login_stage'] = 0
        return login(update, context)


def learning(update, context):
    update.message.reply_text("Вы успешно зашли в свой аккаунт, теперь вы можете использовать весь функционал бота")
    return ConversationHandler.END


if __name__ == "__main__":
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
