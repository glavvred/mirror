""" Database connection and init """
import sqlite3

from sqlalchemy import create_engine, orm
from sqlalchemy.orm import scoped_session, sessionmaker

from settings import DATABASE_PATH, LOGGING_TO_STDOUT


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
        session = scoped_session(sessionmaker())
        echo = False
        if LOGGING_TO_STDOUT:
            echo = True

        engine = create_engine('sqlite:///' + DATABASE_PATH, echo=echo)
        session.configure(bind=engine)
        return session
