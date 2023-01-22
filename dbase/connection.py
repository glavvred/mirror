""" Database connection and init """
import sqlite3

from sqlalchemy import create_engine, orm
from sqlalchemy.orm import sessionmaker, scoped_session

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

    @staticmethod
    def get_scoped_session():
        """
        Get scoped session
        :return: scoped_session
        """
        engine = create_engine('sqlite:///' + DATABASE_PATH)
        session_factory = sessionmaker(bind=engine)
        return scoped_session(session_factory)
