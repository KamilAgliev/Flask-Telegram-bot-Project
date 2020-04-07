"""MyEng - Телеграм бот для узучения английского языка"""
import datetime
from flask import Flask, render_template, jsonify
import datetime
from flask import Flask, render_template, request
from flask_login import LoginManager, login_user, current_user, logout_user, \
    login_required
from flask_restful import Resource, Api, reqparse
from flask_wtf import FlaskForm
from werkzeug.exceptions import abort
from werkzeug.utils import redirect
from wtforms import PasswordField, BooleanField, SubmitField, StringField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
from flask import make_response
from data import db_session
from data.users import User
from resources import users_resources

from data.auth import TOKEN_FOR_TELEGRAM_BOT
# Импортируем необходимые классы.
from telegram.ext import Updater, MessageHandler, Filters, ConversationHandler
from telegram.ext import CallbackContext, CommandHandler

app = Flask(__name__)
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=365)
app.config['SECRET_KEY'] = 'my_secret'

login_manager = LoginManager()
login_manager.init_app(app)
sessionStorage = {}
api = Api(app)


class RegisterForm(FlaskForm):
    stages = ["Введите своё имя", "Введите свою фамилию", "Введите ваш email", "Введите пароль от аккаунта",
              "Повторите пароль от аккаунта", "Введите свой возраст", "Введите ваш адрес"]

    def __init__(self):
        self.surname = ""
        self.name = ""
        self.email = ""
        self.password = ""
        self.password_again = ""
        self.age = -1
        self.address = ""

    def validate_on_submit(self):
        s = db_session.create_session()
        if self.email == "" or self.password == "" or self.surname == "" or self.name == "" or self.age == -1 or self.address == "":
            return "Пожалуйста заполните все поля, это важно!"
        user = s.query(User).filter(User.email == self.email).first()
        if user:
            return "Такой email уже используется!"
        if self.password != self.password_again:
            return "Пароли не совпадают!"


def register(update, context):
    mes = update.message.text
    user_id = update.message.from_user.id
    if user_id in sessionStorage.keys() and sessionStorage[user_id]['has_account'] and sessionStorage[user_id][
        'register_stage'] == 7:
        update.message.reply_text("У вас уже есть аккаунт!")
        sessionStorage[user_id]["login_stage"] = 0
        return login(update, context)
    else:
        if user_id not in sessionStorage.keys():
            form = RegisterForm()
            sessionStorage[user_id] = {
                'has_account': True,
                "register_stage": 0,
                "reg_form": form
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
    sessionStorage[user_id]["reg_form"].addres = mes
    connect = db_session.create_session()
    user = User(
        email=form.email,
        surname=form.surname,
        name=form.name,
        age=form.name,
        address=form.address
    )
    user.set_password(form.password)
    connect.add(user)
    connect.commit()
    sessionStorage[user_id]["login_stage"] = 0
    return login(update, context)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@login_required
def logout():
    logout_user()


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
            login_user(user, remember=True)
            sessionStorage[user_id]['login_stage'] = 0
            return 3
        else:
            update.message.reply_text("Введены неправильные данные, попробуйте ещё раз")
            return 2


def start(update, context):
    update.message.reply_text(
        "Здравствуйте, это бот"
        "для изучения английского языка, \n"
        "для начала вам нужно авторизироваться/зарегистрироваться")
    return 1


def learning(update, context):
    update.message.reply_text("Вы успешно зашли в свой аккаунт, теперь вы можете использовать весь функционал бота")
    return ConversationHandler.END


if __name__ == "__main__":
    db_session.global_init('db/baza.db')
    api.add_resource(users_resources.UsersListResource, '/api/users')
    api.add_resource(users_resources.UsersResource,
                     '/api/users/<int:user_id>')
    app.run()

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
