import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm

from data.db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Test(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'tests'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    theme = sqlalchemy.Column(sqlalchemy.String)  # тема теста
    result = sqlalchemy.Column(sqlalchemy.INTEGER)  # результат прохождения теста (кол во прав ответов)
    questions = orm.relation("Question", back_populates="test")
