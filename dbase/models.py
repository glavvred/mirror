from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Boolean, Time, TIMESTAMP, func
from sqlalchemy.orm import declarative_base, relationship

from dbase.connection import DbConnect

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True

    query = DbConnect.get_scoped_session().query_property()

    id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.current_timestamp())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.current_timestamp())

    def __repr__(self):
        return "<{0.__class__.__name__}(id={0.id!r})>".format(self)


class Condition(BaseModel):
    __tablename__ = "condition"

    text = Column(String(22), unique=True, nullable=False)
    full_text = Column(String(50), unique=False, nullable=False)
    icon = Column(String(20))


class Weather(BaseModel):
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


class WeatherConditions(BaseModel):
    __tablename__ = 'weather_conditions'
    weather_id = Column(ForeignKey(Weather.id, ondelete='CASCADE'), nullable=False, index=True)
    condition_id = Column(ForeignKey(Condition.id, ondelete='CASCADE'), nullable=False, index=True)


class WeatherWithConditions(Weather):
    weather_condition = relationship(Weather, secondary=WeatherConditions.__tablename__, lazy='joined',
                                     remote_side=Weather.id)


class ForecastPart(BaseModel):
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

    condition = Column(String, ForeignKey(Condition.text), nullable=False)


class WeatherForecastPart(BaseModel):
    __tablename__ = "weather_forecast_parts"

    weather_id = Column(Integer, ForeignKey(Weather.id, ondelete='CASCADE'), nullable=False, index=True)
    forecast_part_id = Column(Integer, ForeignKey(ForecastPart.id, ondelete='CASCADE'), nullable=False, index=True)


class WeatherWithForecastParts(Weather):
    forecast_parts = relationship(WeatherForecastPart,
                                  secondary=ForecastPart.__tablename__,
                                  lazy='joined',
                                  primaryjoin=Weather.id == WeatherForecastPart.weather_id,
                                  secondaryjoin=ForecastPart.id == WeatherForecastPart.forecast_part_id
                                  )


class User(BaseModel):
    __tablename__ = "user"

    name = Column(String(100), nullable=False)
    faces = relationship("Face", cascade="all, delete-orphan", backref="user")


class Face(BaseModel):
    __tablename__ = "face"

    filename = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey(User.id, ondelete='CASCADE'), nullable=False, index=True)
