""" weather handling """
import datetime
import sys
import time

import requests

import models
from dbase.connection import DbConnect
from dbase.models import Weather, ForecastPart, Condition
from settings import TIME_ZONE, WEATHER_UPDATE_INTERVAL, YANDEX_API_KEY

from toolbox import ToolBox

session = DbConnect.get_session()
logger = ToolBox.get_logger('weather')


class WeatherMethods:
    """
    weather class
    """
    last_grab = None

    def __init__(self):
        self.stop = None  # stop flag for daemon
        logger.debug('weather daemon initialised')
        last_weather = Weather().get_last()
        if last_weather:
            self.last_grab = last_weather.created_at
        if not self.last_grab:
            self.weather_grab()
            last_id = session.query(Weather).order_by(Weather.id.desc()).first()
            self.last_grab = last_id.created_at

    def start(self):
        """
        main loop
        :return:
        """
        logger.debug('weather daemon started')
        while True:
            if self.stop:
                sys.exit(1)
            time_delta = datetime.datetime.now(tz=TIME_ZONE) - TIME_ZONE.fromutc(self.last_grab)
            if time_delta.seconds > WEATHER_UPDATE_INTERVAL * 60:
                self.weather_grab()
                time.sleep(5)
            else:
                time.sleep(5)

    def weather_grab(self):
        """
        grab and parse
        :return:
        """
        logger.debug('weather grabbing started')
        self.last_grab = datetime.datetime.utcnow()
        headers = {'Content-Type': 'application/json',
                   'X-Yandex-API-Key': YANDEX_API_KEY}
        payload = {
            'lat': 55.755863,
            'lon': 37.6177,
            'lang': 'ru_RU'
        }

        weather_datum = requests.get('https://api.weather.yandex.ru/v2/informers/', params=payload,
                                     headers=headers).json()

        if 'now' in weather_datum:
            fact = weather_datum['fact']
            info = weather_datum['info']
            forecast = weather_datum['forecast']

            weather_data = Weather(
                lat=info['lat'], lon=info['lon'],
                temperature=fact['temp'], feels_like=fact['feels_like'],
                wind_gust=fact['wind_gust'], wind_speed=fact['wind_speed'],
                wind_dir=fact['wind_dir'], pressure=fact['pressure_mm'],
                humidity=fact['humidity'], is_day_time=bool(fact['daytime'] == 'd'),
                season=Weather.SEASON_TO_INT[fact['season']][0],
                sunrise=datetime.time.fromisoformat(forecast['sunrise']),
                sunset=datetime.time.fromisoformat(forecast['sunset']), week=forecast['week'],
                moon=forecast['moon_code']
            )
            condition = session.query(Condition).filter(Condition.text == fact['condition']).first()
            weather_data.condition = condition
            session.add(weather_data)

            for f_part in weather_datum['forecast']['parts']:
                part = ForecastPart(part_name=f_part['part_name'], temp_avg=f_part['temp_avg'],
                                    temp_max=f_part['temp_max'], temp_min=f_part['temp_min'],
                                    feels_like=f_part['feels_like'],
                                    wind_speed=f_part['wind_speed'],
                                    wind_gust=f_part['wind_gust'], wind_dir=f_part['wind_dir'],
                                    pressure=f_part['pressure_mm'], humidity=f_part['humidity'],
                                    prec_mm=f_part['prec_mm'], prec_period=f_part['prec_period'],
                                    prec_prob=f_part['prec_prob'])
                condition = session.query(Condition).filter(
                    Condition.text == f_part['condition']).first()
                part.condition = condition
                weather_data.forecast_parts.append(part)

            session.commit()

            logger.debug('weather grabbing done')
        logger.debug('wait for another day')

    def __del__(self):
        """
        stopped
        :return:
        """
        logger.debug('weather daemon stopped')
