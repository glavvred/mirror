""" main module """
import faulthandler

from flask import Flask

from camera import CameraData

app = Flask(__name__, static_url_path='/static')

faulthandler.enable()
if __name__ == '__main__':
    CameraData().start()
    app.run()
