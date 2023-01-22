import datetime
import time

import requests

from dbase.connection import DbConnect
from dbase.models import Weather, ForecastPart
from dbase.queries import get_last_weather
from settings import *
from toolbox import ToolBox

session = DbConnect.get_session()
logging = ToolBox.get_logger('weather')
seasonToInt = {
    'summer': (1, 'лето'),
    'autumn': (2, 'осень'),
    'winter': (3, 'зима'),
    'spring': (4, 'весна')
}


class WeatherMethods:
    last_grab = None

    def __init__(self):
        logging.debug('weather daemon initialised')
        last_weather = get_last_weather()
        if last_weather:
            self.last_grab = last_weather.created_at
        if not self.last_grab:
            self.weather_grab()
            last_id = session.query(Weather).order_by(Weather.id.desc()).first()
            self.last_grab = last_id.created_at

    def start(self):
        logging.debug('weather daemon started')
        while True:
            time_delta = datetime.datetime.now(tz=TIME_ZONE) - TIME_ZONE.fromutc(self.last_grab)
            if time_delta.seconds > WEATHER_UPDATE_INTERVAL * 60:
                self.weather_grab()
            else:
                time.sleep(1)

    def weather_grab(self):
        logging.debug('weather grabbing started')
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
            humidity=fact['humidity'], is_day_time=True if (fact['daytime'] == 'd') else False,
            season=seasonToInt[fact['season']][0],
            sunrise=datetime.time.fromisoformat(forecast['sunrise']),
            sunset=datetime.time.fromisoformat(forecast['sunset']), week=forecast['week'],
            moon=forecast['moon_code']
        )
        session.add(weather_data)

        for fp in weather_datum['forecast']['parts']:
            part = ForecastPart(part_name=fp['part_name'], condition=fp['condition'],
                                temp_avg=fp['temp_avg'], temp_max=fp['temp_max'],
                                temp_min=fp['temp_min'], feels_like=fp['feels_like'],
                                wind_speed=fp['wind_speed'], wind_gust=fp['wind_gust'],
                                wind_dir=fp['wind_dir'], pressure=fp['pressure_mm'],
                                humidity=fp['humidity'], prec_mm=fp['prec_mm'],
                                prec_period=fp['prec_period'], prec_prob=fp['prec_prob'])
            weather_data.forecast_parts.append(part)

        session.commit()

        logging.debug('weather grabbing done')

    @staticmethod
    def get_current_weather():
        return get_last_weather()
