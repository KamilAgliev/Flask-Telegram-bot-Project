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
    test = orm.relation("Test", back_populates="question")
