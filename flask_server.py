"""MyEng - Телеграм бот для узучения английского языка"""
from flask import jsonify
import datetime
from flask import Flask
from flask_restful import Resource, Api, reqparse
from data import db_session
from data.users import User

app = Flask(__name__)
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=365)
app.config['SECRET_KEY'] = 'my_secret'

api = Api(app)


def log_user(user_id, given_password):
    ses = db_session.create_session()
    user = ses.query(User).filter(User.id == user_id).first()
    if user and user.check_password(given_password):
        return jsonify({"message": 'ok'})
    else:
        return jsonify({"message": "something wrong"})


class RegisterForm:
    stages = [
        "Введите своё имя",
        "Введите свою фамилию",
        "Введите ваш email",
        "Придумайте пароль от аккаунта",
        "Повторите пароль от аккаунта",
        "Введите свой возраст",
        "Введите ваш адрес проживания",
        "Какова ваша цель изучения английского?"
        "\n(путешествия, для работы за границей, разговорный)"
        "\nМожете выбрать несколько, вводите их через запятую(,)."
    ]

    def __init__(self):
        self.surname = ""
        self.name = ""
        self.email = ""
        self.password = ""
        self.password_again = ""
        self.age = -1
        self.address = ""
        self.telegram_name = ""
        self.aim = ""


class UsersResource(Resource):
    def get(self, user_id):
        session = db_session.create_session()
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            return jsonify({"message": "such user does not exist"})
        return jsonify({'user_data': user.to_dict(), "message": "ok"})

    def delete(self, user_id):
        session = db_session.create_session()
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            return jsonify({"message": "such user does not exist"})
        session.delete(user)
        session.commit()
        return jsonify({'message': 'ok, user successfully deleted'})


class UsersListResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('id', type=int, required=True)
    parser.add_argument('surname')
    parser.add_argument('name')
    parser.add_argument('age', type=int)
    parser.add_argument('address')
    parser.add_argument('email')
    parser.add_argument('password')
    parser.add_argument('telegram_name')
    parser.add_argument('aim')

    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify({'users': [item.to_dict() for item in users]})

    def post(self):
        args = UsersListResource.parser.parse_args()
        attributes = ['surname', 'name', 'age', 'address', 'email', 'telegram_name', 'aim']
        session = db_session.create_session()
        exist = session.query(User).filter(User.id == args['id']).first()
        if exist:
            return jsonify({"message": "such user already exists"})
        user = User(
            id=args['id'],
            surname=args['surname'],
            name=args['name'],
            age=args['age'],
            address=args['address'],
            password=args['password'],
            email=args['email'],
            aim=args['aim'],
            telegram_name=args['telegram_name'],
        )
        user.set_password(args['password'])
        session.add(user)
        session.commit()
        return jsonify({'success': 'OK - the user has been added'})


if __name__ == "__main__":
    db_session.global_init('db/baza.db')

    api.add_resource(UsersListResource, '/api/users')
    api.add_resource(UsersResource, '/api/users/<int:user_id>')
    app.run()
