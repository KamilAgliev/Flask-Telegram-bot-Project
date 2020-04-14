import sqlalchemy
from sqlalchemy import orm
from data.db_session import SqlAlchemyBase


class Question(SqlAlchemyBase):
    __tablename__ = 'questions'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    theme = sqlalchemy.Column(sqlalchemy.String)  # тема вопроса
    ru = sqlalchemy.Column(sqlalchemy.String)  # на русском
    en = sqlalchemy.Column(sqlalchemy.String)  # на английском
