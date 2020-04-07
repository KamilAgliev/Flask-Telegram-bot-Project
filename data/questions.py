import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm

from data.db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Question(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'questions'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    theme = sqlalchemy.Column(sqlalchemy.String)  # тема вопроса
    text = sqlalchemy.Column(sqlalchemy.String)  # сам вопрос
    answer = sqlalchemy.Column(sqlalchemy.String)  # ответ на вопрос
    test_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("tests.id"))
    test = orm.relation("Test")
