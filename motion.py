""" motion detection and capture """
import cv2
import imutils
import numpy as np

import settings
from dbase.connection import DbConnect
from toolbox import ToolBox

session = DbConnect.get_session()
logger = ToolBox.get_logger('motion')


class MotionData:
    """
    motion detection and capture
    """
    # глобальная переменная, тащится из camera.py
    frame = settings.LAST_FRAME

    def __init__(self):
        pass

    @staticmethod
    def grey_blur_image(frame):
        """
        make image blurred and grey
        :param frame: image
        :return: image
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        return gray

    def detect_motion(self):
        """
        detect motion
        :return: flag
        """
        logger.debug('motion detection started')
        previous_frame = None
        while True:
            if self.frame:
                current_frame = self.grey_blur_image(
                    cv2.imdecode(np.frombuffer(self.frame, np.uint8), -1))
                settings.MOTION_DETECTED = False
                if previous_frame is None:
                    previous_frame = current_frame

                frame_delta = cv2.absdiff(previous_frame, current_frame)
                thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
                thresh = cv2.dilate(thresh, None, iterations=1)
                contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                            cv2.CHAIN_APPROX_SIMPLE)
                contours = imutils.grab_contours(contours)
                for contour in contours:
                    if cv2.contourArea(contour) > 100000:
                        settings.MOTION_DETECTED = True
