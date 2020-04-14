import sqlalchemy
from sqlalchemy import orm
from data.db_session import SqlAlchemyBase


class Question(SqlAlchemyBase):
    __tablename__ = 'questions'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    theme = sqlalchemy.Column(sqlalchemy.String)  # тема вопроса
    text = sqlalchemy.Column(sqlalchemy.String)  # на русском
    ans = sqlalchemy.Column(sqlalchemy.String)  # на английском
