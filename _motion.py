import cv2
import imutils as imutils
import numpy as np

import settings


class MotionData:
    def __init__(self, app):
        self.app = app
        self.logging = app.logging
        self.storage = app.config["storage"]
        pass

    @staticmethod
    def grey_blur_image(frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        return gray

    def detect_motion(self):
        self.logging.debug('motion detection started')
        previous_frame = None
        while True:
            frame = settings.last_frame
            if frame:
                current_frame = self.grey_blur_image(cv2.imdecode(np.frombuffer(frame, np.uint8), -1))
                settings.motion_detected = False
                if previous_frame is None:
                    previous_frame = current_frame

                frame_delta = cv2.absdiff(previous_frame, current_frame)
                thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
                thresh = cv2.dilate(thresh, None, iterations=1)
                contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                contours = imutils.grab_contours(contours)
                for contour in contours:
                    if cv2.contourArea(contour) > 100000:
                        settings.motion_detected = True
