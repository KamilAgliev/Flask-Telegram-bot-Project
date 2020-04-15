import sqlalchemy
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin

from data.db_session import SqlAlchemyBase


class Question(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'questions'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    theme = sqlalchemy.Column(sqlalchemy.String)  # тема вопроса
    text = sqlalchemy.Column(sqlalchemy.String)  # на русском
    ans = sqlalchemy.Column(sqlalchemy.String)  # на английском
