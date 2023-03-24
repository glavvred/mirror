""" Face finder """
from __future__ import annotations

import array
import string
import time
from os import path, getcwd
from pprint import pprint

# https://github.com/ageitgey/face_recognition
import face_recognition  # pylint: disable=E0401
from sqlalchemy import select

import settings
from dbase.connection import DbConnect
from dbase.models import User
from toolbox import ToolBox

session = DbConnect.get_session()
logging = ToolBox.get_logger('faces')


class FaceData:
    """
    Face finding and recognition class
    """

    def __init__(self):
        self.matched_users = None
        self.faces = []
        self.known_encoding_faces = []
        self.face_user_keys = {}
        self.face_user_names = {}
        self.fading_users = {}
        # init load
        self.load_known()
        self.last_recognize_time = time.time()

    def get_user_by_key(self, user_index: int = 0) -> int | None:
        """
            Get user from known users array
            :param user_index: user_id
            :return: int|None
        """
        if user_index in self.face_user_keys:
            return self.face_user_keys[user_index]
        return None

    def load_known(self):
        """
        Get all users from db and add them to memory for quick access
        :return: None
        """
        results = session.execute(select(User)).all()
        for user_row in results:
            if user_row[0].faces:
                face_image = face_recognition.load_image_file(
                    path.join(settings.IMAGE_STORAGE_TRAINED, user_row[0].faces[0].filename))
                # всегда считаем что на тренировочной фотке одно лицо
                face_image_encoding = face_recognition.face_encodings(face_image)[0]
                index_key = len(self.known_encoding_faces)
                self.known_encoding_faces.append(face_image_encoding)
                self.face_user_keys[index_key] = user_row[0].id
                self.face_user_names[index_key] = user_row[0].name

    def start(self):
        """
            main loop for face recognition daemon
        """
        logging.debug('face recognition daemon started')
        while True:
            self.fade_out()
            if settings.MOTION_DETECTED:
                if time.time() - self.last_recognize_time > settings.CAMERA_RECOGNITION_INTERVAL:
                    self.recognize(settings.LAST_FRAME)

    def recognize(self, captured_image: string = ""):
        """
        Find faces in captured image
        Compare them to known users
        :param captured_image: captured image
        """
        matched_users = []

        start_time = time.time()
        unknown_face_image_locations = face_recognition.face_locations(captured_image)
        # print("--- %s seconds --- 1 " % (time.time() - start_time))
        unknown_face_image_encodings = face_recognition.face_encodings(captured_image, unknown_face_image_locations)
        # print("--- %s seconds --- 2 " % (time.time() - start_time))
        if len(unknown_face_image_encodings) > 0:
            for unknown_face_image_encoding in unknown_face_image_encodings:
                results = face_recognition.compare_faces(
                    self.known_encoding_faces, unknown_face_image_encoding)
                index_key = 0
                for matched in results:
                    if matched:
                        user_id = self.get_user_by_key(index_key)
                        matched_users.append(user_id)
                    index_key = index_key + 1

        for user_id in matched_users:
            print(user_id)
            self.fade_in(user_id)
        # print("IMG RECOGNIZE FPS: ", 1.0 / (time.time() - self.last_recognize_time))
        self.last_recognize_time = time.time()

    def fade_in(self, user_id):
        self.fading_users[user_id] = time.time()
        if user_id not in settings.MATCHED_USERS:
            settings.MATCHED_USERS.append(user_id)
        print('added')

    def fade_out(self):
        for user_id in list(self.fading_users):
            if time.time() > self.fading_users[user_id] + settings.FADE_OUT_TIME:
                self.fading_users.pop(user_id, None)
                settings.MATCHED_USERS.remove(user_id)
                print('removed')
