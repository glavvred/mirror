from __future__ import annotations

import string
from os import path
# https://github.com/ageitgey/face_recognition
import face_recognition
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
        # init load
        self.load_known()

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
                    path.join(settings.IMAGE_STORAGE, 'trained', user_row[0].faces[0].filename))
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
        logging.debug('camera grab daemon started')
        while True:
            if settings.motion_detected:
                self.recognize(settings.last_frame)

    def recognize(self, filename: string = ""):
        """
        Find faces in captured image
        Compare them to known users
        :param filename: captured image
        """
        matched_users = []
        unknown_face_image = face_recognition.load_image_file(
            path.join(settings.IMAGE_STORAGE, 'unknown', filename))
        unknown_face_image_encodings = face_recognition.face_encodings(unknown_face_image)
        if len(unknown_face_image_encodings) > 0:
            for unknown_face_image_encoding in unknown_face_image_encodings:
                results = face_recognition.compare_faces(
                    self.known_encoding_faces, unknown_face_image_encoding)
                index_key = 0
                for matched in results:
                    if matched:
                        matched_users.append(self.get_user_by_key(index_key))
                    index_key = index_key + 1

        self.matched_users = matched_users
