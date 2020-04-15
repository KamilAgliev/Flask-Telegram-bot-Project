import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from data.db_session import SqlAlchemyBase


class Test(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'tests'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    theme = sqlalchemy.Column(sqlalchemy.String)  # тема теста
    questions = sqlalchemy.Column(sqlalchemy.String)
    passed_users = sqlalchemy.Column(sqlalchemy.String)
