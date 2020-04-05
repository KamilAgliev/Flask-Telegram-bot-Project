import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm

from data.db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Teacher(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'teachers'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    user = orm.relation('User')
    alltitude = sqlalchemy.Column(sqlalchemy.INTEGER)  # отношение учеников к учителю от 0 до 10
    my_students = orm.relation("Student")
