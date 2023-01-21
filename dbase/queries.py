from dbase.connection import DbConnect
from dbase.models import Weather, WeatherWithForecastParts

session = DbConnect.get_session()


def get_last_weather():
    weather = session.query(Weather).filter(WeatherWithForecastParts.forecast_parts).order_by(
        Weather.id.desc()).first()

    return weather

