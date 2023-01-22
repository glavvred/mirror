import os
from os import path, getcwd

import pytz

# Microphone stream config.
CHUNK = 1024  # CHUNKS of bytes to read each time from mic
FORMAT = 8
CHANNELS = 1
RATE = 16000
THRESHOLD = 1000  # The threshold intensity that defines silence
# and noise signal (an int. lower than THRESHOLD is silence).

SILENCE_LIMIT = 2  # Silence limit in seconds. The max amount of seconds where
# only silence is recorded. When this time passes the
# recording finishes and the file is delivered.
PREV_AUDIO = 0.5  #

FILE_ALLOWED = ['image/png', 'image/jpeg']
IMAGE_STORAGE = path.join(getcwd(), 'upload')
AUDIO_STORAGE = path.join(getcwd(), 'recordings')
AUDIO_FILENAME = 'record.wav'
WEATHER_UPDATE_INTERVAL = 30  # minutes
YANDEX_API_KEY = '8c9073a2-a106-4136-9cf8-54396aaf625f'
CAMERA_ID = 1
CAMERA_INTERVAL = 0.5
last_frame = None
motion_detected = None

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = f'{ROOT_DIR}\\dbase\\test_db.db'

TIME_ZONE = pytz.timezone('Europe/Moscow')
SQLALCHEMY_SILENCE_UBER_WARNING = 1
INTENTS = 'models/intents.json'
