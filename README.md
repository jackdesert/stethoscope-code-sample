stethoscope
===========


Ingest RSSI readings from badges

Predict location based on this data.


Getting Started
---------------

- Change directory into your newly created project.

    cd stethoscope

- Create a Python virtual environment.

    python3 -m venv env

- Upgrade packaging tools.

    env/bin/pip install --upgrade pip setuptools

- Install the project in editable mode with its testing requirements.

    env/bin/pip install -e ".[testing]"

- Configure the database.

    env/bin/initialize_stethoscope_db development.ini

- Run your project's tests.

    env/bin/pytest

- Run your project.

    env/bin/pserve development.ini



Prerequisites
-------------

  * Python3
  * redis-py https://github.com/andymccurdy/redis-py

    python3 -m pip install --user redis

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

    curl -k -X POST -H "Content-Type:application/json"  -i http://localhost:6543/rssi_readings   -d '{"badge_id":"2","pi_id":"2"}'



BACKLOG
-------

* Return proper status codes
* Index action


