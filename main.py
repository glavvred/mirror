""" main module """
import faulthandler

from flask import Flask, render_template

from dbase.models import Weather
from users import UserMethods

app = Flask(__name__, static_url_path='/static')

faulthandler.enable()


@app.route('/api/users/new', methods=['POST'])
def users_new():
    """
    new user
    """
    return UserMethods().new_user().emit()


@app.route('/api/users/<int:user_id>', methods=['GET', 'DELETE'])
def users_get(user_id):
    """
    get user/delete user
    """
    return UserMethods().get_user(user_id).emit()


@app.route('/api/weather/show')
def weather():
    """
    show weather
    """
    weather_data = Weather.get_last()
    return render_template('weather.html', weather_data=weather_data)


if __name__ == '__main__':
    app.run()
