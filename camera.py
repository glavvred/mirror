""" Module camera recorder """
import time

import cv2  # pylint: disable=E0401

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
    camera_id = None

    def __init__(self):
        self.stopped = False
        self.last_grab = time.time() - 1
        # DSHOW( and MSMF) are windows only.
        # on linux, use V4L, FFMPEG or GSTREAMER
        self.get_camera_id()
        if self.camera_id not in range(0, settings.CAMERA_ID_MAX):
            self.stop()
        logger.debug(f'current camera id is {self.camera_id}')
        self.stream = cv2.VideoCapture(self.camera_id, cv2.CAP_DSHOW)
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        logger.debug('camera grab daemon initialised')

    def get_camera_id(self):
        """
        check if any camera present at 0-10 slots
        """
        for camera_id in range(0, settings.CAMERA_ID_MAX):
            stream = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
            if stream.isOpened():
                self.camera_id = camera_id
                stream.release()
                return

    def start(self):
        """
        Main loop for image capturing daemon
        Loop for camera image grab
        :return:  jpeg to global variable settings.last_frame
        """
        logger.debug('camera grab daemon started')
        while True:
            if self.stopped:
                print('stopped by flag')
                return
            if time.time() - self.last_grab > 0:
                # print("CAM GRAB FPS: ", 1.0 / (time.time() - self.last_grab))
                (self.grabbed, self.frame) = self.stream.read()
                if self.grabbed:
                    small_frame = cv2.resize(self.frame, (0, 0), fx=0.25, fy=0.25)
                    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
                    rgb_small_frame = small_frame[:, :, ::-1]
                    settings.LAST_FRAME = rgb_small_frame
                self.last_grab = time.time()
            else:
                time.sleep(settings.CAMERA_INTERVAL)

    def stop(self):
        """
        Stop image grabbing flag
        :return: None
        """
        logger.debug('camera grab daemon stopping')
        self.stopped = True
        cv2.destroyAllWindows()

    def __del__(self):
        """
        If crashed, stop service
        :return: None
        """
        self.stop()
