import faulthandler
import threading

from flask import Flask, render_template
from audio import AudioRecorder
from path import check_and_create_directories
from toolbox import *

from camera import CameraData
from faces import FaceData
from users import UserData
from weather import WeatherMethods
from motion import MotionData
from speech import VoiceData

app = Flask(__name__, static_url_path='/static')


# routes

@app.route('/api/users/new', methods=['POST'])
def users_new():
    return UserData().new_user().emit()


@app.route('/api/users/<int:user_id>', methods=['GET', 'DELETE'])
def users_get(user_id):
    return UserData().get_user(user_id).emit()


@app.route('/api/weather/show')
def weather():
    weather_data = WeatherMethods().get_current_weather()
    return render_template('weather.html', weather_data=weather_data)


if __name__ == '__main__':
    faulthandler.enable()
    logger = ToolBox().get_logger("main", logging.DEBUG)

    thread = threading.Thread(name='weather_daemon', target=WeatherMethods().start)
    thread.setDaemon(True)
    thread.start()

    camera_status = CameraData().test_camera()
    logger.debug('Checking camera: %s ', camera_status)
    if camera_status == 'Available':
        c_d = threading.Thread(name='camera_daemon', target=CameraData().start)
        c_d.setDaemon(True)
        c_d.start()
        m_d = threading.Thread(name='motion_daemon', target=MotionData().detect_motion)
        m_d.setDaemon(True)
        m_d.start()
        fr_d = threading.Thread(name='face_recognition_daemon', target=FaceData().start)
        fr_d.setDaemon(True)
        fr_d.start()

    check_and_create_directories()

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
