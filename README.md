[![DeepSource](https://static.deepsource.io/deepsource-badge-light-mini.svg)](https://deepsource.io/gh/delivey/AnO/?ref=repository-badge)
# Affairs-and-Order

Affairs & order is a nation simulation game, where you can make your own nation, build a military and industry, and declare war.

# Repo installation.

1. Install Git and add Git to PATH. https://stackoverflow.com/questions/26620312/installing-git-in-path-with-github-client-for-windows
2. Type `git clone https://github.com/delivey/AnO.git` in the folder you want the repo to be cloned in.

# Flask

1. Install Python (Preferrably 3.8) https://www.python.org/downloads/release/python-380/.
2. Run `pip install -r requirements.txt`, this will install all the modules needed for this repo.
3. Type `flask run` in this repo's folder on your own PC.
4. Navigate to `http://127.0.0.1:5000/` or the url flask gave you in your browser. The website should run

# PostgresQL

### Windows
1. Get the `.exe` installer from here: https://www.enterprisedb.com/downloads/postgres-postgresql-downloads. Download version 12.3
2. Run the installer, leave the default port and other default settings, set your password as `ano`
3. Run this command in the `psql` terminal: `\i C:\Users\user\Desktop\AnO\affo\dump.sql` replace the path with your path for `dump.sql`.

# RabbitMQ

### Arch

1. Install rabbitmq by typing `pacman -S rabbitmq`
2. Follow this guide: https://docs.celeryproject.org/en/stable/getting-started/brokers/rabbitmq.html and name your username, password and vhost `ano`
3. Run rabbitmq by typing: `sudo rabbitmq-server`

### Debian

1. Follow this guide to install RabbitMQ: https://www.vultr.com/docs/how-to-install-rabbitmq-on-ubuntu-16-04-47 and name your username, password and vhost `ano`
2. Stop the rabbitmqctl service for naming usernames, vhosts, etc by typing: `sudo rabbitmqctl stop`
3. Run the RabbitMQ broker by typing: `sudo rabbitmq-server`

# Celery

#### IMPORTANT NOTE: open all your terminals using `sudo -i`, this will give root access to celery.
1. Navigate into the `AnO` folder.
2. Run `celery -A app.celery worker --loglevel=INFO --pidfile=''` in a terminal window.
3. Run `celery -A app.celery beat --loglevel=INFO --pidfile=''` in yet another terminal window.
4. For celery to work, you've gotta run Flask in yet another terminal window. You can do so by typing: `flask run` in a different terminal window.
