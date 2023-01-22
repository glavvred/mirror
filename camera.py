""" Module camera recorder """
import time

import cv2

import settings
from dbase.connection import DbConnect
from toolbox import ToolBox

session = DbConnect.get_session()
logger = ToolBox.get_logger('camera')


class CameraData:
    """
    Camera capture daemon
    """
    stopped = False
    grabbed = None
    frame = None

    def __init__(self):
        logger.debug('camera grab daemon initialised')
        self.last_grab = time.time() - 1
        # DSHOW( and MSMF) are windows only.
        # on linux, use V4L, FFMPEG or GSTREAMER
        self.stream = cv2.VideoCapture(settings.CAMERA_ID, cv2.CAP_DSHOW)

    def is_camera_available(self) -> bool:
        """
        Test if camera is available
        :return: bool
        """
        if self.stream is None or not self.stream.isOpened():
            self.stop()
            return False
        return True

    def start(self):
        """
        Main loop for image capturing daemon
        :return: None
        """
        logger.debug('camera grab daemon started')
        while True:
            if time.time() - self.last_grab > 1:
                self.read()
            else:
                time.sleep(settings.CAMERA_INTERVAL)

    def read(self):
        """
        Loop for camera image grab
        :return: jpeg to global variable settings.last_frame
        """
        while True:
            if self.stopped:
                return
            (self.grabbed, self.frame) = self.stream.read()
            if self.grabbed:
                _, jpeg = cv2.imencode('.jpg', self.frame)
                settings.last_frame = jpeg.tobytes()

    def stop(self):
        """
        Stop image grabbing flag
        :return: None
        """
        logger.debug('camera grab daemon stopping')
        self.stopped = True

    def __del__(self):
        """
        If crashed, stop service
        :return: None
        """
        self.stop()
