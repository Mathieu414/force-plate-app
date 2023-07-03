# import dependencies
# manage database
import sqlite3
from sqlalchemy import Table, create_engine
from sqlalchemy.sql import select
from flask_sqlalchemy import SQLAlchemy

conn = sqlite3.connect("data.sqlite")
# connect to the database
engine = create_engine("sqlite:///data.sqlite")
db = SQLAlchemy()


# class for the table Users
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(80))


Users_tbl = Table("users", Users.metadata)


# fuction to create table using Users class
def create_users_table():
    Users.metadata.create_all(engine)


def drop_users_table():
    Users.__table__.drop(engine)
