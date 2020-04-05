"""MyEng - Телеграм бот для узучения английского языка"""
import datetime
from flask import Flask, render_template, jsonify
import datetime
from flask import Flask, render_template, request
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from flask_restful import Resource, Api, reqparse
from flask_wtf import FlaskForm
from werkzeug.exceptions import abort
from data import db_session
from data.users import User

app = Flask(__name__)
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=365)
app.config['SECRET_KEY'] = 'my_secret'

api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


def log_user(user):
    load_user(user)


@login_required
def logout():
    logout_user()


class RegisterForm:
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


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    users = session.query(User).get(user_id)
    if not users:
        abort(404, message=f"Users {user_id} not found")


class UsersResource(Resource):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        return jsonify({'users': user.to_dict()})

    def delete(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK - user deleted'})


class UsersListResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('surname', required=True)
    parser.add_argument('name', required=True)
    parser.add_argument('age', required=True, type=int)
    parser.add_argument('address', required=True)
    parser.add_argument('email', required=True)
    parser.add_argument('password', required=True)

    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify({'users': [item.to_dict() for item in users]})

    def post(self):
        args = UsersListResource.parser.parse_args()
        session = db_session.create_session()
        user = User(
            surname=args['surname'],
            name=args['name'],
            age=args['age'],
            address=args['address'],
            email=args['email'],
        )
        user.set_password(args['password'])
        session.add(user)
        session.commit()
        return jsonify({'success': 'OK - the user has been added'})


if __name__ == "__main__":
    db_session.global_init('db/baza.db')
    api.add_resource(UsersListResource, '/api/users')
    api.add_resource(UsersResource,
                     '/api/users/<int:user_id>')
    app.run()
