import datetime
from os import path

from flask import request
from sqlalchemy import select
from werkzeug.utils import secure_filename

import settings
from dbase.connection import DbConnect
from dbase.models import User, Face
from toolbox import *

session = DbConnect.get_session()
logging = ToolBox.get_logger('weather')


class UserData:
    def __init__(self):
        pass

    @staticmethod
    def delete_user_by_id(user_id: int):
        user = session.execute(select(User).filter(User.id == user_id)).first()
        if not user:
            return False
        user = user[0]
        session.delete(user)
        session.commit()
        return True

    def get_user(self, user_id):
        user = session.execute(select(User).filter(User.id == user_id)).first()[0]
        if not user:
            return ApiResponseHandle('found none', 404)
        user = user[0]

        if request.method == 'GET':
            return ApiResponseHandle('user found: ' + str(user.id))
        if request.method == 'DELETE':
            self.delete_user_by_id(user.id)
            return ApiResponseHandle('deleted', 200)

    @staticmethod
    def new_user():
        if 'image' not in request.files:
            output = {"success": False, "reason": "Image field requested"}
            return ApiResponseHandle(output, 200)

        file = request.files['image']
        if file.mimetype not in settings.FILE_ALLOWED:
            output = {"success": False, "reason": "Image mimetype is not in list"}
            return ApiResponseHandle(output, 500)

        filename = "_".join([datetime.datetime.now().strftime("%y%m%d_%H%M%S"), secure_filename(file.filename)])
        file.save(path.join(settings.IMAGE_STORAGE, 'trained', filename))

        new_user = User(request.form['name'])
        new_face = Face(filename)
        new_user.faces.append(new_face)
        session.add(new_user)
        session.commit()

        return ApiResponseHandle('all good')
