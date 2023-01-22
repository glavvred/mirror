import sqlite3
from os import path, getcwd

from sqlalchemy import create_engine, orm

sqlite3_path = path.join(getcwd(), f'dbase\\test_db.db')


def get_connection():
    return sqlite3.connect(sqlite3_path)


def get_session():
    engine = create_engine('sqlite:///' + sqlite3_path)
    return orm.Session(bind=engine)
