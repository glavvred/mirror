import datetime
from os import path
from flask import request

from werkzeug.utils import secure_filename

from dbase.connection import DbConnect
from dbase.models import User, Face
import settings
from toolbox import *

session = DbConnect.get_session()
logging = ToolBox.get_logger('weather')


class UserData:
    def __init__(self):
        pass

    def delete_user_by_id(self, user_id: int):
        user = session.query(User).filter(User.id == user_id).first()
        print(user)
        # User.query.filter(User.id == user_id).delete()
        # Face.query.filter(Face == user_id).delete()
        return True

    def get_user_by_id(self, user_id):
        with self.connection as connection:
            user = connection.execute("SELECT * FROM user WHERE id = ?", str(user_id)).fetchone()
            if user:
                return user[0]
            else:
                return None

    def get_user(self, user_id):
        user = self.get_user_by_id(user_id)
        if request.method == 'GET':
            if user:
                return ApiResponseHandle('user found: ' + str(user.id))
            else:
                return ApiResponseHandle('found none', 404)

        if request.method == 'DELETE':
            self.delete_user_by_id(user_id)
            if user:
                return ApiResponseHandle('deleted', 200)
            else:
                return ApiResponseHandle('found none', 404)

    def new_user(self):
        if 'image' not in request.files:
            output = {"success": False, "reason": "Image field requested"}
            return ApiResponseHandle(output, 200)

        file = request.files['image']
        if file.mimetype not in self.app.config['file_allowed']:
            output = {"success": False, "reason": "Image mimetype is not in list"}
            return ApiResponseHandle(output, 500)

        filename = "_".join(
            [datetime.datetime.now().strftime("%y%m%d_%H%M%S"), secure_filename(file.filename)])
        file.save(path.join(self.app.config['storage'], 'trained', filename))

        with self.connection as connection:
            new_user_id = connection.execute("SELECT id FROM user ORDER BY id DESC LIMIT 1; ").fetchone()
            if new_user_id:
                new_user_id = new_user_id[0] + 1
            else:
                new_user_id = 1
            connection.execute("INSERT INTO user (id, name, dt) VALUES (?, ?, ?)", (new_user_id, request.form['name'],
                                                                                    datetime.datetime.now()))
            connection.execute("insert into face (filename, dt, user_id) VALUES (?, ?,?)", (filename,

                                                                                            datetime.datetime.now(),
                                                                                            request.form['name']))

        return ApiResponseHandle('all good')


UserData().delete_user_by_id(1)
