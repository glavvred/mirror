import logging
import time
import cv2
import settings
from dbase.connection import DbConnect
from toolbox import ToolBox

session = DbConnect.get_session()
logging = ToolBox.get_logger('camera')


class CameraData:
    stopped = False

    def __init__(self):
        logging.debug('camera grab daemon initialised')
        self.last_grab = time.time() - 1
        # DSHOW( and MSMF) are windows only.
        # on linux, use V4L, FFMPEG or GSTREAMER
        self.stream = cv2.VideoCapture(settings.CAMERA_ID, cv2.CAP_DSHOW)

    def test_camera(self):
        if self.stream is None or not self.stream.isOpened():
            self.stop()
            return "Failed"
        return "Available"

    def start(self):
        logging.debug('camera grab daemon started')
        while True:
            if time.time() - self.last_grab > 1:
                self.read()
            else:
                time.sleep(settings.CAMERA_INTERVAL)

    def read(self):
        logging.debug('camera grab image')
        while True:
            if self.stopped:
                return
            (self.grabbed, self.frame) = self.stream.read()
            if self.grabbed:
                ret, jpeg = cv2.imencode('.jpg', self.frame)
                settings.last_frame = jpeg.tobytes()

    def stop(self):
        logging.debug('camera grab daemon stopping')
        self.stopped = True

    def __del__(self):
        self.stop()
