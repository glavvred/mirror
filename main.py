import datetime
import faulthandler
import threading

from flask import Flask, Response, render_template
import settings
from toolbox import *

from _camera import CameraData
from _faces import FaceMethods
from weather import WeatherMethods
from _motion import MotionData
from _speech import VoiceData, AudioRecorder
from _user import UserMethods

app = Flask(__name__, static_url_path='/static')
settings.init(app)


# routes

@app.route('/api/users/new', methods=['POST'])
def users_new():
    return UserMethods().new_user().emit()


@app.route('/api/users/<int:user_id>', methods=['GET', 'DELETE'])
def users_get(user_id):
    return UserMethods().get_user(user_id).emit()


@app.route('/api/weather/show')
def weather():
    weather_data, forecast_parts = WeatherData(app).show_weather()
    return render_template('weather.html', weather_data=weather_data, forecast_parts=forecast_parts)


if __name__ == '__main__':
    faulthandler.enable()
    app.logging = ToolBox().get_logger("main", logging.DEBUG)

    # thread = threading.Thread(name='weather_daemon', target=WeatherData(app).start)
    # thread.setDaemon(True)
    # thread.start()
    #
    # camera_status = CameraData(app).test_camera()
    # app.logging.debug('Checking camera: %s ', camera_status)
    # if camera_status == 'Available':
    #     c_d = threading.Thread(name='camera_daemon', target=CameraData(app).start)
    #     c_d.setDaemon(True)
    #     c_d.start()
    #     m_d = threading.Thread(name='motion_daemon', target=MotionData(app).detect_motion)
    #     m_d.setDaemon(True)
    #     m_d.start()
    #     fr_d = threading.Thread(name='face_recognition_daemon', target=FaceData(app).start)
    #     fr_d.setDaemon(True)
    #     fr_d.start()
    #
    # # почистить папку с записями, создать ее
    audio_recorded = threading.Event()
    ar_d = threading.Thread(name='audio_recording_daemon', target=AudioRecorder(audio_recorded).start)
    ar_d.setDaemon(True)
    ar_d.start()
    vr_d = threading.Thread(name='voice_recognition_daemon', target=VoiceData(audio_recorded).start)
    vr_d.setDaemon(True)
    vr_d.start()

    while True:
        pass
    # app.run(debug=True)
