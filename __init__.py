from flask import Flask
from flask_sqlalchemy import SQLAlchemy

DEBUG = True  # Turns on debugging features in Flask
BCRYPT_LOG_ROUNDS = 12  # Configuration for the Flask-Bcrypt extension
MAIL_FROM_EMAIL = "robert@example.com"  # For use in application emails

app = Flask(__name__, instance_relative_config=True)

app.config.from_pyfile('config.py')
print(app.config)

db = SQLAlchemy(app)
