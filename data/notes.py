import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase



class Notes(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'notes'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"), nullable=True)
    bit_picture = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    location = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    information = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    date = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True)
    is_anon = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)
    like = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    user = orm.relationship('User')