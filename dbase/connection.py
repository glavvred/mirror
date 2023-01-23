""" Database connection and init """
import sqlite3

from sqlalchemy import create_engine, orm

from settings import DATABASE_PATH


class DbConnect:
    """
    Database class
    """

    @staticmethod
    def get_connection():
        """
        get connection
        :return: Sqlite3.connection
        """
        return sqlite3.connect(DATABASE_PATH)

    @staticmethod
    def get_session():
        """
        Get session
        :return: orm.Session
        """
        engine = create_engine('sqlite:///' + DATABASE_PATH)
        return orm.Session(bind=engine)
