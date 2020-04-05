import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm

from data.db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Test(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'tests'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    theme = sqlalchemy.Column(sqlalchemy.String)  # тема теста
    making_student = orm.relation("Student")  # ученик, который делал тест
    result = sqlalchemy.Column(sqlalchemy.INTEGER)  # результат прохождения теста (кол во прав ответов)
    made_time = sqlalchemy.Column(sqlalchemy.String) # время когда был сделан тест (Unix time)
    questions = orm.relation("Question")
