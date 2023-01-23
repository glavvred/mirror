""" main module """
import faulthandler
import logging
import threading

from flask import Flask, render_template

from audio import AudioRecorder
from camera import CameraData
from faces import FaceData
from motion import MotionData
from path import create_folders_if_not_exist
from speech import VoiceData
from toolbox import ToolBox

from users import UserMethods
from weather import WeatherMethods
from dbase.models import Weather

app = Flask(__name__, static_url_path='/static')


# routes

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
    weather_data = Weather.get_current()
    return render_template('weather.html', weather_data=weather_data)


if __name__ == '__main__':
    faulthandler.enable()
    logger = ToolBox().get_logger("main", logging.DEBUG)

    thread = threading.Thread(name='weather_daemon', target=WeatherMethods().start)
    thread.setDaemon(True)
    thread.start()

    CAMERA_STATUS = CameraData().is_camera_available()
    logger.debug('Checking camera: %s ', CAMERA_STATUS)
    if CAMERA_STATUS:
        c_d = threading.Thread(name='camera_daemon', target=CameraData().start)
        c_d.setDaemon(True)
        c_d.start()
        m_d = threading.Thread(name='motion_daemon', target=MotionData().detect_motion)
        m_d.setDaemon(True)
        m_d.start()
        fr_d = threading.Thread(name='face_recognition_daemon', target=FaceData().start)
        fr_d.setDaemon(True)
        fr_d.start()

    create_folders_if_not_exist()

    audio_recorded = threading.Event()
    ar_d = threading.Thread(name='audio_recording_daemon',
                            target=AudioRecorder(audio_recorded).start)
    ar_d.setDaemon(True)
    ar_d.start()
    vr_d = threading.Thread(name='voice_recognition_daemon', target=VoiceData(audio_recorded).start)
    vr_d.setDaemon(True)
    vr_d.start()

    while True:
        pass
    # app.run(debug=True)
