import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps
from celery import Celery

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def make_celery(app): # celery -A app.celery worker
    celery = Celery(
        app.import_name,
        CELERY_BROKER_URL="redis://127.0.0.1:6379/0",
        CELERY_RESULT_BACKEND="redis://127.0.0.1:6379/0"
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery