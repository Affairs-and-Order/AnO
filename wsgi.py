from app import flapp

if __name__ == "__main__":
    flapp.run()

# run with gunicorn by using: gunicorn --bind 0.0.0.0:5000 wsgi:app