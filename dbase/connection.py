import sqlite3
from sqlalchemy import create_engine, orm
from sqlalchemy.orm import sessionmaker, scoped_session

from settings import DATABASE_PATH


class DbConnect:
    @staticmethod
    def get_connection():
        return sqlite3.connect(DATABASE_PATH)

    @staticmethod
    def get_session():
        engine = create_engine('sqlite:///' + DATABASE_PATH)
        return orm.Session(bind=engine)

    @staticmethod
    def get_scoped_session():
        engine = create_engine('sqlite:///' + DATABASE_PATH)
        session_factory = sessionmaker(bind=engine)
        return scoped_session(session_factory)
