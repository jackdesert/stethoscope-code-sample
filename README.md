Stethoscope
===========

A room-by-room location predictor based on badges RSSI readings.

* Post badge RSSI readings to Stethoscope via the API (see docs/api.md)
* View recent RSSI readings at /.
* Eventually Stethoscope will be able to predict in which room a particular
badge is located.


Technologies
------------

### Python

This project is written in Python. Python is a strong choice because it
has excellent data science libraries (including deep learning libraries
like keras).


### Pyramid

Pyramid is a framework with more flexibilty than Django
(meaning it will let us use SQLAlchemy)
but more structure than Flask.


### SQLAlchemy

SQLAlchemy is the object-relational mapper.


### CookieCutter

This project was jump-started with the [pyramid-cookiecutter-alchemy](https://github.com/Pylons/pyramid-cookiecutter-alchemy) cookiecutter.











---
---
---

Installation
------------

### Python3.6 required

Version 3.6 is required because this project uses f-strings.


    python3 --version

If you have 3.6 or later, you may skip to the next section.

If you have 3.5 or earlier, see doc/pyenv.md
to install pyenv and python 3.6 or later.

Once you have python 3.6 or later installed, use that version
of python when invoking `python3 -m venv env` in the "Getting Started"
section below.

Once you invoke venv to create the sandboxed "venv", you can
delete the .python-version file that was probably created
when you called `pyenv local 3.6.x`




### Install Other Prerequisites

    sudo apt install -y htop nginx python3-venv redis-server




Getting Started (This step generated from cookiecutter)
-------------------------------------------------------

- Change directory into your newly created project.

    cd stethoscope

- Create a Python virtual environment.

    # This must be done with python 3.6 or later
    # because this project uses f-strings
    python3 -m venv env

- Upgrade packaging tools [and redis, markdown]

    env/bin/pip install --upgrade pip setuptools redis markdown requests

- Install the project in editable mode with its testing requirements.

    env/bin/pip install -e ".[testing]"

- Configure the database.

    env/bin/initialize_stethoscope_db development.ini

- Run your project's tests.

    env/bin/pytest

- Run your project.

    env/bin/pserve development.ini


Redis
-----

This project uses redis as part of its deduplication scheme.
Docs are at https://github.com/andymccurdy/redis-py


Nginx
-----

    cd /etc/nginx/sites-enabled
    sudo rm default
    sudo ln -s /home/ubuntu/stethoscope/config/bip-stethoscope-nginx.conf
    sudo nginx -s reload


### Nginx Server Tokens

It's considered more secure to not broadcast "nginx (version)/(os_version)" with each request.
Open /etc/nginx/nginx.conf and uncomment this line:

    server_tokens off;


Systemd
-------

Stethoscope runs on the waitress webserver, which is easy to set up on systemd.

    cd /lib/systemd/system
    sudo ln -s /home/ubuntu/config/stethoscope.service
    sudo systemctl enable stethoscope.service
    sudo systemctl start stethoscope.service


SSL via Let's Encrypt
---------------------

https://certbot.eff.org/


Testing
-------

    env/bin/pytest



Performance Load Testing
------------------------

see tools/README.md and tools/generate_load_test.py.

In short, on an EC2 nano box running waitress via systemd,
this app stands up to 400 total requests/second, of which 20/second
write to the database. (5% unique)

This is enough to collect data in 5 houses simultaneously.

Note this did not include load from location prediction, because
as of July 12, 2018 that piece has not been built yet.


Smoothie Charts
-------------

http://smoothiecharts.org/

Note that as of July 15, 2018 we are using a modified version of smoothie,
available at https://github.com/jackdesert/smoothie/blob/display_series_label_in_tooltip/smoothie.js

See the pull request at https://github.com/joewalnes/smoothie/pull/107


---
---
---

Other Pieces that May Need Implementing to Move This Project Forward
====================================================================



Get Person IDs (So we can map badges to people)
-----------------------------------------------

GET staging.elitecare.com/api/badges_people.json

Now we know which badge maps to which person_id



Set Locations (To Acquire Training Data)
----------------------------------------

POST staging.elitecare.com/api/location

payload: [{person_id: xxx, room_id: xxx}, ...]



API
---

    curl -k -X POST -H "Content-Type:application/json"  -i http://localhost:6543/rssi_readings   -d '{"badge_id":"1", "pi_id":"2", "beacons":{"a": -30, "b": -35, "c": -40} }'




uWSGI
-----

Here is the invocation of the entry point defined by wsgi.py

    sudo uwsgi --chmod-socket=020 --enable-threads --plugin=python3 -s /home/ubuntu/stethoscope/tmp/stethoscope.sock --manage-script-name --mount /=wsgi:app --uid ubuntu --gid www-data --virtualenv env




SECURITY and PRODUCTION
-----------------------

Some things to address before going live in production:

  * Lock down IP address (Elitecare + Jack + Tony + Bill + our EC2 boxen + site24x7)
    - Is this necessary?
    - what about site24x7




BACKLOG
-------

  * Find out where timezone is set for database
    - at one point new readings were showing up as "7 hours ago"
  * Make it clear which page you are on
  * Think about ways of visualizing the data coming in
    - allow download of sqlite database?
  * Architect where button press data will go. Elitecarerails?
  * Get pyramid to return 500 when server breaks (currently returns 404)
  * Slack notifications when something breaks
  * RATIONALE
    - why waitress
    - why sqlite
    - why pyramid
    - why python
    - why filter



