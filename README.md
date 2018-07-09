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

    env/bin/pip install --upgrade pip setuptools redis markdown

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




SECURITY and PRODUCTION
-----------------------

Some things to address before going live in production:

  * Lock down IP address (Elitecare + Jack + Tony + Bill + our EC2 boxen + site24x7)
  * Move to production.ini
  * Move to postgres (at least for production)
  * Load test (vegeta)
  * Decide whether we want persistent data when we stop the box.
  * Get pyramid to return 500 when server breaks (currently returns 404)
  * uWSGI / emperor / systemd
  * Get index page to load from site24x7
    - it it really feasible to lock this down via IP address?



Subdomain Names Considered
--------------------------

    bip-ble
    bip-data
    bip-data-science
    bip-deep-learning
    bip-gps
    bip-locale
    bip-loran
    bip-orion
    bip-scidata
    bip-science
    bip-stethoscope (stethoscope is the name of the project repo)



BACKLOG
-------

* Make it clear which page you are on


