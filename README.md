stethoscope
===========


Ingest RSSI readings from badges

Predict location based on this data.


Install pyenv and Python 3.6
----------------------------

Install pyenv and python 3.6+. See doc/pyenv.md
Version 3.6 is required because this project uses f-strings.

    cd /path/to/stethoscope
    pyenv local 3.6.6



Install Other Prerequisites
---------------------------

    sudo apt install -y htop nginx python3-venv redis-server




Getting Started
---------------

- Change directory into your newly created project.

    cd stethoscope

- Create a Python virtual environment.

    python3 -m venv env

- Upgrade packaging tools [and redis]

    env/bin/pip install --upgrade pip setuptools redis

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

redis-py is required: https://github.com/andymccurdy/redis-py


Nginx
-----

    cd /etc/nginx/sites-enabled
    sudo ln -s /home/ubuntu/stethoscope/config/bip-stethoscope-nginx.conf
    sudo nginx -s reload


SSL via Let's Encrypt
---------------------

https://certbot.eff.org/


Nginx Server Tokens
-------------------

It's considered more secure to not broadcast "nginx (version)/(os_version)" with each request.
Open /etc/nginx/nginx.conf and uncomment this line:

    server_tokens off;



Get Person IDs
--------------

GET staging.elitecare.com/api/badges_people.json

Now we know which badge maps to which person_id


Set Locations
-------------

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


BACKLOG
-------

* Return proper status codes
* Index action


