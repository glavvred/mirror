import sqlite3
from sqlalchemy import create_engine, orm
from settings import DATABASE_PATH


class DbConnect:
    @staticmethod
    def get_connection():
        return sqlite3.connect(DATABASE_PATH)

    @staticmethod
    def get_session():
        engine = create_engine('sqlite:///' + DATABASE_PATH)
        return orm.Session(bind=engine)
