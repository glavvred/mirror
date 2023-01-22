""" database models """
from sqlalchemy import Column, Integer, String, ForeignKey, Float, Boolean, Time, TIMESTAMP, func
from sqlalchemy.orm import declarative_base, relationship

# pylint: disable=import-error
from dbase.connection import DbConnect
# pylint: enable=import-error

Base = declarative_base()
session = DbConnect.get_session()


class BaseModel(Base):
    """
    Base model for all classes
    """
    __abstract__ = True

    id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now(),
                        onupdate=func.current_timestamp())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(),
                        onupdate=func.current_timestamp())

    def __repr__(self):
        return "<{0.__class__.__name__}(id={0.id!r})>".format(self)


class Condition(BaseModel):
    """
    weather conditions
    """
    __tablename__ = "condition"

    text = Column(String(22), unique=True, nullable=False)
    full_text = Column(String(50), unique=False, nullable=False)
    icon = Column(String(20))


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

    condition = Column(String, ForeignKey(Condition.text), nullable=False)
    forecast_parts = relationship("ForecastPart", cascade="all, delete-orphan", backref="weather")

    def get_last(self):
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
    weather = relationship("Weather", backref="forecast_parts")
    condition = Column(String, ForeignKey(Condition.text), nullable=False)


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
