""" weather handling """
import datetime
import time

import requests

from dbase.connection import DbConnect
from dbase.models import Weather, ForecastPart
from dbase.queries import get_last_weather
from settings import TIME_ZONE, WEATHER_UPDATE_INTERVAL, YANDEX_API_KEY

from toolbox import ToolBox

session = DbConnect.get_session()
logger = ToolBox.get_logger('weather')
seasonToInt = {
    'summer': (1, 'лето'),
    'autumn': (2, 'осень'),
    'winter': (3, 'зима'),
    'spring': (4, 'весна')
}


class WeatherMethods:
    """
    weather class
    """
    last_grab = None

    def __init__(self):
        logger.debug('weather daemon initialised')
        last_weather = get_last_weather()
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
            time_delta = datetime.datetime.now(tz=TIME_ZONE) - TIME_ZONE.fromutc(self.last_grab)
            if time_delta.seconds > WEATHER_UPDATE_INTERVAL * 60:
                self.weather_grab()
            else:
                time.sleep(1)

    def weather_grab(self):
        """
        grab and parse
        :return:
        """
        logger.debug('weather grabbing started')
        self.last_grab = time.time()
        headers = {'Content-Type': 'application/json',
                   'X-Yandex-API-Key': YANDEX_API_KEY}
        payload = {
            'lat': 55.755863,
            'lon': 37.6177,
            'lang': 'ru_RU'
        }

        weather_datum = requests.get('https://api.weather.yandex.ru/v2/informers/', params=payload,
                                     headers=headers).json()

        fact = weather_datum['fact']
        info = weather_datum['info']
        forecast = weather_datum['forecast']

        weather_data = Weather(
            lat=info['lat'], lon=info['lon'],
            temperature=fact['temp'], feels_like=fact['feels_like'], wind_gust=fact['wind_gust'],
            wind_speed=fact['wind_speed'], wind_dir=fact['wind_dir'], pressure=fact['pressure_mm'],
            humidity=fact['humidity'], is_day_time=bool(fact['daytime'] == 'd'),
            season=seasonToInt[fact['season']][0],
            sunrise=datetime.time.fromisoformat(forecast['sunrise']),
            sunset=datetime.time.fromisoformat(forecast['sunset']), week=forecast['week'],
            moon=forecast['moon_code']
        )
        session.add(weather_data)

        for f_part in weather_datum['forecast']['parts']:
            part = ForecastPart(part_name=f_part['part_name'], condition=f_part['condition'],
                                temp_avg=f_part['temp_avg'], temp_max=f_part['temp_max'],
                                temp_min=f_part['temp_min'], feels_like=f_part['feels_like'],
                                wind_speed=f_part['wind_speed'], wind_gust=f_part['wind_gust'],
                                wind_dir=f_part['wind_dir'], pressure=f_part['pressure_mm'],
                                humidity=f_part['humidity'], prec_mm=f_part['prec_mm'],
                                prec_period=f_part['prec_period'], prec_prob=f_part['prec_prob'])
            weather_data.forecast_parts.append(part)

        session.commit()

        logger.debug('weather grabbing done')

    @staticmethod
    def get_current_weather():
        """
        get weather
        :return:
        """
        return get_last_weather()
