# The script to run if Celery or RabbitMQ fails.
import os

current_dir = os.getcwd()
new_dir = current_dir.replace("\\scripts", "")
os.chdir(new_dir)
import tasks

