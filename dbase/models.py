""" database models """
from typing import Any

from sqlalchemy import Column, Integer, String, ForeignKey, Float, Boolean, Time, TIMESTAMP, func
from sqlalchemy.orm import declarative_base, relationship
from dbase.connection import DbConnect  # pylint: disable=import-error

Base = declarative_base()
session = DbConnect.get_session()


class BaseModel(Base):
    """
    Base model for all classes
    """
    __abstract__ = True
    SEASON_TO_INT = {
        'summer': (1, 'лето'),
        'autumn': (2, 'осень'),
        'winter': (3, 'зима'),
        'spring': (4, 'весна')
    }

    id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now(),
                        onupdate=func.current_timestamp())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(),
                        onupdate=func.current_timestamp())

    def __str__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id!r})>"


class Condition(BaseModel):
    """
    weather conditions
    """
    __tablename__ = "condition"

    text = Column(String(22), unique=True, nullable=False)
    full_text = Column(String(50), unique=False, nullable=False)
    icon = Column(String(20))

    @staticmethod
    def fill_base_data():
        """
        fill base data for conditions
        :return:
        """
        clear = Condition(text='clear', full_text='ну ясно', icon='day-sunny')
        partly_cloudy = Condition(text='partly-cloudy', full_text='ну почти ясно',
                                  icon='day-cloudy')
        cloudy = Condition(text='cloudy', full_text='облачка', icon='day-cloudy')
        overcast = Condition(text='overcast', full_text='тучки', icon='day-sunny-overcast')
        drizzle = Condition(text='drizzle', full_text='хрень с неба', icon='sprinkle')
        light_rain = Condition(text='light-rain', full_text='чуть капает', icon='rain-mix')
        rain = Condition(text='rain', full_text='льет', icon='rain')
        moderate_rain = Condition(text='moderate-rain', full_text='поливает', icon='rain')
        heavy_rain = Condition(text='heavy-rain', full_text='заливает', icon='thunderstorm')
        continuous_rain = Condition(text='continuous-heavy-rain', full_text='вымокнешь',
                                    icon='thunderstorm')
        showers = Condition(text='showers', full_text='точно вымокнешь', icon='showers')
        wet_snow = Condition(text='wet-snow', full_text='снего-дождь', icon='showers')
        light_snow = Condition(text='light-snow', full_text='слегка снег', icon='snow')
        snow = Condition(text='snow', full_text='прям снег', icon='snow')
        snow_showers = Condition(text='snow-showers', full_text='метель', icon='snow-wind')
        hail = Condition(text='hail', full_text='град', icon='hail')
        ts = Condition(text='thunderstorm', full_text='гремит', icon='thunderstorm')
        ts_rain = Condition(text='thunderstorm-with-rain', full_text='гремит и льет',
                            icon='thunderstorm')
        ts_hail = Condition(text='thunderstorm-with-hail', full_text='погодное бинго',
                            icon='thunderstorm')

        session.add_all(
            [clear, partly_cloudy, cloudy, overcast, drizzle, light_snow, light_rain, rain,
             moderate_rain, heavy_rain, continuous_rain, showers, wet_snow, snow, snow_showers,
             hail,
             ts, ts_hail, ts_rain])
        session.commit()


class Weather(BaseModel):
    """
    weather itself
    """
    __tablename__ = 'weather'

    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)

    temperature = Column(Integer, nullable=False)
    feels_like = Column(Integer, nullable=False)

    wind_speed = Column(Integer, nullable=False)
    wind_gust = Column(Integer, nullable=False)
    wind_dir = Column(String(2), nullable=False)

    pressure = Column(Integer, nullable=False)
    humidity = Column(Integer, nullable=False)

    is_day_time = Column(Boolean, nullable=False)
    season = Column(String(6), nullable=False)

    sunrise = Column(Time, nullable=False)
    sunset = Column(Time, nullable=False)
    week = Column(Integer, nullable=False)
    moon = Column(Integer, nullable=False)

    condition_text = Column(String, ForeignKey(Condition.text), nullable=False)
    condition = relationship(Condition, foreign_keys=[condition_text])
    forecast_parts = relationship("ForecastPart", cascade="all, delete-orphan")

    @staticmethod
    def get_last():
        """
        get last weather
        :return:
        """
        weather = session.query(Weather).order_by(Weather.id.desc()).first()
        return weather


class ForecastPart(BaseModel):
    """
    forecast
    """
    __tablename__ = "forecast_part"

    part_name = Column(String, nullable=False)

    temp_avg = Column(Integer, nullable=False)
    temp_max = Column(Integer, nullable=False)
    temp_min = Column(Integer, nullable=False)

    feels_like = Column(Integer, nullable=False)

    wind_speed = Column(Integer, nullable=False)
    wind_gust = Column(Integer, nullable=False)
    wind_dir = Column(String(2), nullable=False)

    pressure = Column(Integer, nullable=False)
    humidity = Column(Integer, nullable=False)

    prec_mm = Column(Integer, nullable=False)
    prec_period = Column(Integer, nullable=False)
    prec_prob = Column(Integer, nullable=False)

    weather_id = Column(Integer, ForeignKey(Weather.id), nullable=False)
    condition_text = Column(String, ForeignKey(Condition.text), nullable=False)
    condition = relationship(Condition, foreign_keys=[condition_text])


class User(BaseModel):
    """
    user
    """
    __tablename__ = "user"

    name = Column(String(100), nullable=False)
    faces = relationship("Face", cascade="all, delete-orphan", backref="user")


class Face(BaseModel):
    """
    face of user
    """
    __tablename__ = "face"

    filename = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey(User.id, ondelete='CASCADE'), nullable=False, index=True)


class News(BaseModel):
    """
       news
       """
    __tablename__ = "news"

    source = Column(String, nullable=True)
    author = Column(String, nullable=True)
    title = Column(String, nullable=False)

    @staticmethod
    def get_last(quantity=None):
        """
        get last news grab
        :return:
        """
        if quantity:
            return session.query(News).order_by(News.id.desc()).limit(quantity).all()
        return session.query(News).order_by(News.id.desc()).first()
