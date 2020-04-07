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
from data.questions import Question
from data.tests import Test
from data.users import User

# import langid
# print(langid.classify("Привет"))

WORDS_FOR_LEARNING = {
    'Путешествия': {
        "inception": "Знакомство с новой страной нередко начинается именно с аэропорта."
                     " Чтобы вы не растерялись, мы составили список слов,"
                     " которые вам наверняка пригодятся во время регистрации на рейс и по прилете.",
        "themes": [{"title": "Английский для туристов в дороге",
                    "youtude_title": "О том, как проходить таможенный контроль",
                    "youtube_urls": ["https://www.youtube.com/watch?v=pgjfHxFj2_I"],
                    "words": ["the check-in desk  стойка регистрации",
                              "self check-in point  место для самостоятельной регистрации",
                              "passport control  паспортный контроль",
                              "customs	таможня", "immigration enquiries  иммиграционный контроль",
                              "arrivals, arrivals hall  зона прилета", "a ticket	билет",
                              "a boarding pass	посадочный талон",
                              "airline enquiries	справочная служба аэропорта",
                              "lost and found	бюро находок", "baggage drop-off	зона сдачи багажа",
                              "baggage claim, baggage reclaim	зона выдачи багажа",
                              "an international flight	международный рейс",
                              "a domestic flight	внутренний рейс",
                              "transfer	трансфер", "departures, departures hall	зона вылета"],
                    "test_id": 1,
                    "test_title": "Приезд / аеропорт"
                    }
            , {"title": "Оказавшись в гостинице, вам необходимо подойти на стойку"
                        " регистрации (reception) и узнать о размещении (accommodation)."
                        " Если вы бронировали жилье, скажите: Hello! I have a reservation."
                        " My surname is Ivan Ivanov. — Здравствуйте! У меня есть бронь. Меня зовут Иван Иванов."
                        "Вот ещё фразы для этого случая",
               "youtude_title": "В гостинице",
               "youtube_urls": ["https://www.youtube.com/watch?v=sQlEvZIdTms"],
               "words": [['Hello, can I reserve a room, please? ', 'Здравствуйте, могу ли я забронировать номер?'],
                         ['Can I book a room? ', 'Могу ли я забронировать номер?'],
                         ['What types of rooms are available? ', 'Какие номера свободны?'],
                         ['I’m leaving in ', '5 days. Я уезжаю через 5 дней.'],
                         ['I would like to book a single room', 'Я бы хотел зарезервировать одноместный номер'],
                         ['What’s the price for a single room?', 'Какова стоимость одноместного номера?'],
                         ['I’d like to book a room overviewing the sea/lake. ',
                          'Я бы хотел забронировать номер с видом на море/озеро.'],
                         ['I’d like full board ', '/ half-board. Я бы хотел полный пансион / полупансион.'],
                         ['May I have a late check-out? ', 'Могу ли я попросить поздний выезд?'],
                         ['Do you have a car park? ', 'У вас есть парковка?'],
                         ['Does the hotel have a gym ', '/ swimming pool? В отеле есть тренажерный зал / бассейн?'],
                         ['Do you have a special menu for children? ', 'У вас есть специальное меню для детей?'],
                         ['Does the hotel have any facilities for children? ',
                          'В отеле есть развлечения (услуги) для детей?'],
                         ['Do you allow pets? ', 'Разрешаете ли вы заселяться с домашними животными?'],
                         ['Does the hotel provide airport transfer? ', 'Отель обеспечивает трансфер из/до аэропорта?'],
                         ['How much is the service charge and tax? ', 'Сколько стоит обслуживание и налог?'],
                         ['Is there anything cheaper? ', 'Есть что-то подешевле?'],
                         ['What is the total cost? ', 'Какова итоговая сумма к оплате?'],
                         ['smoking allowed ', 'разрешено курить'],
                         ['a rental ', 'сумма арендной платы'],
                         ['a single room ', 'комната на одного человека'],
                         ['a double room ', 'комната на двоих с общей кроватью'],
                         ['a twin room ', 'комната на двоих с раздельными кроватями'],
                         ['a crib ', 'детская кроватка'],
                         ['free parking ', 'бесплатная парковка'],
                         ['amenities ', 'удобства'],
                         ['heating ', 'отопление'],
                         ['a fireplace ', 'камин'],
                         ['a kitchen ', 'кухня'],
                         ['a fridge ', 'холодильник'],
                         ['dishes ', 'посуда'],
                         ['cutlery ', 'столовые приборы'],
                         ['a stove ', 'плита'],
                         ['an oven ', 'духовка'],
                         ['a dishwasher ', 'посудомоечная машина'],
                         ['cable TV ', 'кабельное ТВ'],
                         ['an iron ', 'утюг'],
                         ['bed linen ', 'постельное белье'],
                         ['toiletries ', 'ванные принадлежности'],
                         ['towels ', 'полотенца'],
                         ['a garden ', 'сад'],
                         ['a pool ', 'бассейн'],
                         ['pets allowed ', 'можно останавливаться с животными'],
                         ['check-in time ', 'время заезда'],
                         ['check-out time ', 'время выезда']],
               "test_id": 2,
               "test_title": "В гостинице"
               },
                   {"title": "Исследуем город",
                    "youtude_title": "Как быть в иностранном городе",
                    "youtube_urls": ["https://www.youtube.com/watch?v=cp_5Z3RUnow",
                                     "https://www.youtube.com/watch?v=J6gWridhh64"],
                    "words": [
                        ['a cathedral ', 'собор'],
                        ['a square ', 'площадь'],
                        ['a mosque ', 'мечеть'],
                        ['a church ', 'церковь'],
                        ['a town hall ', 'ратуша'],
                        ['a castle ', 'замок'],
                        ['a palace ', 'дворец'],
                        ['a temple ', 'храм'],
                        ['a tower ', 'башня'],
                        ['a museum ', 'музей'],
                        ['a statue ', 'статуя'],
                        ['a monument ', 'памятник'],
                        ['a sculpture ', 'скульптура'],
                        ['a park ', 'парк'],
                        ['a fountain ', 'фонтан'],
                        ['an art gallery ', 'художественная галерея'],
                        ['a ballet ', 'балет'],
                        ['an opera ', 'опера'],
                        ['a theatre ', 'театр'],
                        ['a cinema ', 'кинотеатр'],
                        ['a circus ', 'цирк'],
                        ['a zoo ', 'зоопарк'],
                        ['a stadium ', 'стадион'],
                        ['a canyon ', 'каньон'],
                        ['a cave ', 'пещера'],
                        ['beautiful ', 'красивый'],
                        ['crowded ', 'переполненный'],
                        ['packed with tourist ', 'забит туристами'],
                        ['lovely ', 'милый, чудный'],
                        ['unique ', 'уникальный'],
                        ['spectacular ', 'захватывающий'],
                        ['picturesque ', 'красочный'],
                        ['remarkable ', 'выдающийся'],
                        ['impressive ', 'впечатляющий'],
                        ['charming ', 'очаровательный'],
                        ['Could you tell me how to get to the National museum? ',
                         'Вы не могли бы сказать мне, как добраться до национального музея?'],
                        ['How can I get to the supermarket? ', 'Как мне добраться до супермаркета?'],
                        ['Where is the nearest bus/subway station? ', 'Где находится ближайший автовокзал/метро?'],
                        ['Is there an ATM ', '/ cash machine near here? Здесь поблизости есть банкомат?'],
                        ['Where is the nearest bus stop? ', 'Где находится ближайшая автобусная остановка?'],
                        ['How can I get to Hilton Hotel? ', 'Как я могу добраться до отеля Hilton?'],
                        ['Which bus/train goes to the Blue Mosque from here? ',
                         'Какой автобус/поезд идет до Голубой мечети отсюда?'],
                        ['What is the best way to get around London? ', 'Какой лучший способ перемещаться по Лондону?'],
                        ['Go straight ', '(on). Идите прямо.'],
                        ['Turn left. ', 'Поверните налево.'],
                        ['Turn left at the corner. ', 'На углу поверните налево.'],
                        ['Turn right. ', 'Сверните направо.'],
                        ['Turn right at the crossroads/intersection. ', 'На перекрестке поверните направо.'],
                        ['Cross the street. ', 'Перейдите дорогу.'],
                        ['Continue along Bank Street until you see the cinema. ',
                         'Продолжайте (идти) вдоль Bank Street, пока не увидите кинотеатр.'],
                        ['Then turn left. ', 'Затем поверните налево.'],
                        ['After that take Oxford Street. ', 'После этого идите по / держитесь Oxford Street.'],
                        ['When you get to the bridge, you’ll see the National museum. ',
                         'Когда вы доберетесь до моста, вы увидите Национальный музей.'],
                        ['At the corner of the street you will see the National museum. ',
                         'На углу улицы вы увидите Национальный музей.'],
                        ['It is next to... ', 'Это рядом с...'],
                        ['The cinema is next to the park. ', 'Кинотеатр находится рядом с парком.'],
                        ['It is far from here/near hear. ', 'Это далеко/близко отсюда.'],
                        ['The bank is between... ', 'Банк находится между...'],
                        ['The railway station is between the bank and the theatre. ',
                         'Железнодорожный вокзал находится между банком и театром.'],
                        ['It is across from/opposite... ', 'Это по другую сторону / напротив...'],
                        ['The shop you are looking for is across from/opposite the church. ',
                         'Магазин, который вы ищите, находится напротив церкви.'],
                    ],
                    "test_id": 3,
                    "test_title": "исследуем город"
                    },
                   {"title": "Английский для туристов в ресторане",
                    "youtude_title": "О том, как быть в ресторане",
                    "youtube_urls": ["https://www.youtube.com/watch?v=ZObNbpRhpGc"],
                    "words": [
                        ['I’ve booked a table. ', 'Я бронировал столик.'],
                        ['Do you have any free tables? I need a table for two. ',
                         'У вас есть свободные столики? Мне нужен столик на двоих.'],
                        ['May I sit here? ', 'Я могу сесть здесь?'],
                        ['Can I get a table by the window? ', 'Можно мне столик у окна?'],
                        ['Could we get an extra chair? ', 'Можно нам еще один стул?'],
                        ['Can I have the menu, please? ', 'Можно мне меню, пожалуйста?'],
                        ['Where can I see a list of drinks? ', 'Где я могу найти список напитков?'],
                        ['What dish can you recommend? ', 'Какое блюдо вы могли бы посоветовать?'],
                        ['What do you recommend? ', 'Что вы порекомендуете?'],
                        ['We are ready to order. ', 'Мы готовы сделать заказ.'],
                        ['I am not ready yet. ', 'Я еще не готов.'],
                        ['I would like a cup of coffee. ', 'Я бы хотел чашечку кофе.'],
                        ['A glass of water, please. ', 'Стакан воды, пожалуйста.'],
                        ['I would like the set lunch. ', 'Я бы хотел комплексный обед.'],
                        ['Can I have a steak, please? ', 'Можно мне стейк, пожалуйста?'],
                        ['What are the side dishes? ', 'Какие есть гарниры?'],
                        ['What is this dish? ', 'Что это за блюдо?'],
                        ['', 'Если у вас есть особые пожелания, используйте следующие фразы:'],
                        ['I am allergic to nuts. Does this dish contain nuts? ',
                         'У меня аллергия на орехи. Это блюдо содержит орехи?'],
                        ['I am a vegetarian. Do you have any vegetarian food? ',
                         'Я вегетарианец. У вас есть вегетарианская еда?'],
                        ['Can I get this burger without onion? ', 'Можно мне этот бургер без лука?'],
                        ['Could I change my order? I would like a salad instead of meat. ',
                         'Я могу изменить заказ? Я бы хотел салат вместо мяса.'],
                        ['I am in a hurry. How long will I have to wait for the order? ',
                         'Я спешу. Сколько мне придется ждать заказ?'],
                        ['', 'Воспользуйтесь следующими фразами, чтобы расплатиться:'],
                        ['Can I have the bill/check, please? ', 'Могу ли я получить счет?'],
                        ['Could I pay by credit card/in cash? ', 'Можно заплатить картой/наличными?'],
                        ['Could you check the bill for me, please? It does not seem right. ',
                         'Не могли бы вы проверить мой счет, пожалуйста? Кажется, в нем ошибка.'],
                        ['Is service included? ', 'Обслуживание включено в счет?'],
                        ['I am paying for everybody. ', 'Я плачу за всех.'],
                        ['Can we pay separately? ', 'Можем мы заплатить раздельно?'],
                        ['Keep the change. ', 'Сдачи не надо.'],
                    ],
                    "test_id": 4,
                    "test_title": "В ресторане"
                    },
                   {"title": "Английский для туристов в магазине",
                    "youtude_title": "Английский для туристов в магазине",
                    "youtube_urls": ["https://www.youtube.com/watch?v=t4hHFNWjtk4",
                                     ['https://www.youtube.com/watch?v=LLpnmrbjnjI']],
                    "words": [['Where is the nearest souvenir shop / shopping mall / market? ',
                               'Где находится ближайший сувенирный магазин / торговый центр / рынок?'],
                              ['Sorry, can you help me, please? ', 'Прошу прощения, вы можете мне помочь?'],
                              ['How much is it? ', 'How much is it?'],
                              ['How much does it cost? ', 'Сколько это стоит?'],
                              ['Do you have a special offer? ', 'У вас есть специальное предложение?'],
                              ['Are there any discounts? ', 'А скидки есть?'],
                              ['Okay, I’ll take it. ', 'Хорошо, я беру/покупаю.'],
                              ['Where can I pay for it? ', 'Где я могу рассчитаться за это?'],
                              ['Can you give me a receipt? ', 'Можете выдать мне чек?'],
                              ['Where is a shop assistant? ', 'Где продавец-консультант?'],
                              ['I don’t see a price tag. ', 'Я не вижу ценник.'],
                              ['Can I pay for it by card? ', 'Я могу расплатиться за это картой?'],
                              ['',
                               'Если хотите обновить гардероб, смело идите в любой магазин одежды (a clothes shop), ведь мы подготовили необходимые для этого фразы на английском:'],
                              ['I am looking for a shirt/dress/T-shirt. ', 'Я ищу рубашку/платье/футболку.'],
                              ['Do you have this suit in white? ', 'Этот костюм есть в белом цвете?'],
                              ['I would like to try it on. ', 'Я бы хотел примерить это.'],
                              ['Excuse me, where is the fitting room/changing room? ',
                               'Извините, где находится примерочная?'],
                              ['Where can I try this coat on? ', 'Где я могу примерить это пальто?'],
                              ['Do you have this jacket in S/M/L size? ',
                               'У вас есть этот пиджак/куртка в размере S/M/L?'],
                              ['Can you give me a bigger/smaller size? ',
                               'Вы не могли бы дать мне размер побольше/поменьше?'],
                              ['',
                               'Если вы захотите вернуть или обменять товар, вооружитесь чеком и следующими выражениями:'],
                              ['I need to take this dress back to the shop. ',
                               'Мне нужно вернуть это платье в магазин.'],
                              ['I would like to get a refund. ', 'Я бы хотел получить возврат.'],
                              ['I would like to change it. I have bought the wrong size. ',
                               'Я бы хотел поменять это. Я купил неправильный размер.']],
                    "test_id": 5,
                    "test_title": "Приезд / аеропорт"
                    }],

    }, 'бизнес': {

    }, "разговорный": {

    }
}

app = Flask(__name__)
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=365)
app.config['SECRET_KEY'] = 'my_secret'

api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app) \
 \
@ login_manager.user_loader


def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


def log_user(user_id, given_password):
    ses = db_session.create_session()
    user = ses.query(User).filter(User.id == user_id).first()
    if user and user.check_password(given_password):
        load_user(user.id)
        return jsonify({"message": 'ok'})
    else:
        return jsonify({"message": "something wrong"})


@login_required
def logout():
    logout_user()


class RegisterForm:
    stages = ["Введите своё имя", "Введите свою фамилию", "Введите ваш email", "Придумайте пароль от аккаунта",
              "Повторите пароль от аккаунта", "Введите свой возраст", "Введите ваш адрес проживания",
              "Какова ваша цель изучения английского?"
              "\n(путешествия, бизнес, разговорный)"
              "\nЭто не сильно повлияет на обучение в целом."]

    def __init__(self):
        self.surname = ""
        self.name = ""
        self.email = ""
        self.password = ""
        self.password_again = ""
        self.age = -1
        self.address = ""
        self.position = ""
        self.aim = ""

    def validate_on_submit(self):
        s = db_session.create_session()
        if self.email == "" or self.password == "" or self.surname == "" or self.name == "" or self.age == -1 or self.address == "":
            return "Пожалуйста заполните все поля, это важно!"
        user = s.query(User).filter(User.email == self.email).first()
        if user:
            return "Такой email уже используется!"
        if self.password != self.password_again:
            return "Пароли не совпадают!"


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
        return jsonify({'message': 'ok'})


class UsersListResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('id', required=True, type=int)
    parser.add_argument('surname', required=True)
    parser.add_argument('name', required=True)
    parser.add_argument('age', required=True, type=int)
    parser.add_argument('address', required=True)
    parser.add_argument('email', required=True)
    parser.add_argument('password', required=True)
    parser.add_argument('position', required=True)
    parser.add_argument('aim', required=True)

    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify({'users': [item.to_dict() for item in users]})

    def post(self):
        args = UsersListResource.parser.parse_args()
        session = db_session.create_session()
        user = User(
            id=args['id'],
            surname=args['surname'],
            name=args['name'],
            age=args['age'],
            address=args['address'],
            email=args['email'],
            aim=args['aim'],
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
