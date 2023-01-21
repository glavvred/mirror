import logging
import time
import cv2
import settings

last_frame = None


class CameraData:
    def __init__(self, app):
        self.app = app
        self.logging = app.logging
        self.logging.debug('camera grab daemon initialised')
        self.last_grab = time.time() - 1
        # DSHOW( and MSMF) are windows only.
        # on linux, use V4L, FFMPEG or GSTREAMER
        self.stream = cv2.VideoCapture(app.config['camera_id'], cv2.CAP_DSHOW)
        self.stopped = False
        self.update_started = False

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
                time.sleep(1)

    def read(self):
        self.logging.debug('camera grab image')
        while True:
            if self.stopped:
                return
            (self.grabbed, self.frame) = self.stream.read()
            if self.grabbed:
                ret, jpeg = cv2.imencode('.jpg', self.frame)
                settings.last_frame = jpeg.tobytes()

    def stop(self):
        self.logging.debug('camera grab daemon stopping')
        self.stopped = True

    def __del__(self):
        self.stop()
