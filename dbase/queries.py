""" db queries funcs """
from dbase.connection import DbConnect
from dbase.models import Weather

session = DbConnect.get_session()


def get_last_weather():
    """
    get last weather
    :return:
    """
    weather = session.query(Weather).order_by(Weather.id.desc()).first()

    return weather
