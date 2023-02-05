""" main module """
import faulthandler
import logging
import threading

from flask import Flask, render_template
from dbase.connection import DbConnect

from audio import AudioRecorder
from camera import CameraData
from faces import FaceData
from motion import MotionData
from speech import VoiceData
from toolbox import ToolBox

from users import UserMethods
from weather import WeatherMethods
from dbase.models import Weather, Condition

faulthandler.enable()
app = Flask(__name__, static_url_path='/static')

logger = ToolBox().get_logger("main", logging.DEBUG)

session = DbConnect.get_session()
if session.query(Condition).count() == 0:  # пустая таблица condition
    Condition.fill_base_data()
ToolBox.create_folders_if_not_exist()


thread = threading.Thread(name='weather_daemon', target=WeatherMethods().start)
thread.setDaemon(True)
thread.start()


c_d = threading.Thread(name='camera_daemon', target=CameraData().start)
c_d.setDaemon(True)
c_d.start()
m_d = threading.Thread(name='motion_daemon', target=MotionData().detect_motion)
m_d.setDaemon(True)
m_d.start()
fr_d = threading.Thread(name='face_recognition_daemon', target=FaceData().start)
fr_d.setDaemon(True)
fr_d.start()


audio_recorded = threading.Event()
ar_d = threading.Thread(name='audio_recording_daemon',
                        target=AudioRecorder(audio_recorded).start)
ar_d.setDaemon(True)
ar_d.start()
vr_d = threading.Thread(name='voice_recognition_daemon', target=VoiceData(audio_recorded).start)
vr_d.setDaemon(True)
vr_d.start()


@app.route('/api/users/new', methods=['POST'])
def users_new():
    """
    new user
    """
    return UserMethods().new_user().emit()


@app.route('/api/users/<int:user_id>', methods=['GET', 'DELETE'])
def users_get(user_id):
    """
    get user/delete user
    """
    return UserMethods().get_user(user_id).emit()


@app.route('/api/weather/show')
def weather():
    """
    show weather
    """
    weather_data = Weather.get_last()
    return render_template('weather.html', weather_data=weather_data)


if __name__ == '__main__':
    app.run()
