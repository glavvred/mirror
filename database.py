from os import path, getcwd
from sqlalchemy import create_engine, orm

sqlite3_path = path.join(getcwd(), f'dbase\\test_db.db')


def get_session() -> orm.Session:
    """
        Get session
    :return: orm.Session
    """
    engine = create_engine('sqlite:///' + sqlite3_path)
    return orm.Session(bind=engine)
