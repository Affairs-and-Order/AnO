from src import app

if __name__ == "__main__":
    app.run()

# run with gunicorn by using: gunicorn --bind 0.0.0.0:5000 wsgi:app
