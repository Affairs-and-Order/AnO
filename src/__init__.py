from flask import Flask
from tempfile import mkdtemp
from flask_session import Session

app = Flask(__name__)

# basic cache configuration
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config["CELERY_BROKER_URL"] = 'amqp://ano:ano@localhost:5672/ano'
app.config["CELERY_RESULT_BACKEND"] = 'amqp://ano:ano@localhost:5672/ano'

# import routes

from .authentication import login, signup
