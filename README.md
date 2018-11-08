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

    sudo apt install -y htop nginx python3-venv redis-server postgresql




Getting Started (This step generated from cookiecutter)
-------------------------------------------------------

- Change directory into your newly created project.

    cd stethoscope

- Create a Python virtual environment.

    # This must be done with python 3.6 or later
    # because this project uses f-strings
    python3 -m venv env

- Upgrade packaging tools [and specific packages]

    # If trouble installing tensorflow, omit "--upgrade" option
    env/bin/pip install --upgrade pip ipdb setuptools redis markdown requests alembic numpy keras tensorflow psycopg2

- Install the project in editable mode with its testing requirements.

    env/bin/pip install -e ".[testing]"

- Configure the database.

    env/bin/initialize_stethoscope_db development.ini

- Run your project's tests.

    env/bin/pytest

- Run your project.

    KERAS_BACKEND=theano env/bin/pserve development.ini --reload


Postgresql (Optional)
---------------------

#TODO does user need to be a superuser?

Create a mortal user
  sudo -u postgres createuser steth

Set password and create database
  sudo -u postgres psql
  > \password steth
  > create database steth with owner steth;
  CREATE DATABASE



Alternatively, connect to any database that already exists (shown here
connecting to database named "postgres") so you can create the database
  sudo -u postgres psql postgres -U steth
  > create database





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

Note that we use IP whitelisting. See the nginx config file.


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


Schema Migrations
-----------------

Uses alembic for schema migrations.

    env/bin/alembic upgrade head


Timezone
--------

Database timestamps are naive. That is, they are set without timezone information.

However, Python respects the `TZ` environment variable.

Therefore, if you want your naive database timestamps to match the clock
in a particular timzezone (Pacific is easiest for us), just set the `TZ`
environment variable.

Set it in your systemd unit file, if you run from systemd.
Set it in your ~/.bashrc if you invoke manually.


Performance Load Testing of POST /rssi_readings
-----------------------------------------------

see tools/README.md and tools/generate_load_test.py.

In short, on an EC2 nano box running waitress via systemd,
this app stands up to 400 total requests/second, of which 20/second
write to the database. (5% unique)

This is enough to collect data in 5 houses simultaneously.

Note this did not include load from location prediction, because
as of July 12, 2018 that piece has not been built yet.


Simple Load Testing of /location
--------------------------------

    echo GET http://localhost:6540/badges/2/location | vegeta attack -rate 50 -duration 1s  | vegeta report


Smoothie Charts
-------------

http://smoothiecharts.org/

Note that as of July 15, 2018 we are using a modified version of smoothie,
available at https://github.com/jackdesert/smoothie/blob/display_series_label_in_tooltip/smoothie.js

See the pull request at https://github.com/joewalnes/smoothie/pull/107



Slack Integration
-----------------

If the environment variable POST_TO_SLACK is set, any unhandled exceptions
will be handled by the custom exception view defined in stethoscope/views/exception.py.



Train the Keras Model using TrainingRuns
----------------------------------------

When you are ready to train a large dataset, it is recommended to
download the sqlite database to your local machine (which likely
has more memory than the production box) and train the keras model locally.

Afterward, simply push keras/model.h5 and keras/metadata.pickle
to your production box.


Train but do not save:

    env/bin/python stethoscope/models/neural_network.py

Train and save to disk:

    env/bin/python stethoscope/models/neural_network.py --save


Re-Training with Additional Beacons
-----------------------------------

Let's say you want to add more beacons to an already-trained system.
The most likely scenario is that you decide to support additional rooms,
and you didn't have any beacons in or near those rooms previously.

The most conservative answer for best accuracy is to delete all
training runs, then create new training runs from scratch.

However, it is obviously most convenient to simple add the new beacons,
create new training runs only for the newly added rooms, and go on your
merry way.

### How to Tell if it Will be Worth Re-Training

Say you already trained rooms A, B, and C with beacons R, S, T, and U.
If you now train a new room D with additional beacons V and W,
the new room D will have shiny new (accurate) training runs. It's the
training runs for rooms A, B, and C that are in question. Here's
how to tell if it's worth re-training A, B, and C:

* With beacons V and W turned on, go into each of rooms A, B, and C with a badge
and watch the data coming in from that badge at /badges/:id.

* In each of rooms A, B, and C what you are looking for is whether
beacons V and W show up strongly. If they do, delete the training
runs for that room and create them anew. If they do not, it's fine
to leave them be.

(Note that beacons V and W, if present in the RssiReading, will show up in the
"imposter_beacons" part of the payload at /badges/:id. But what you
are actually looking for is whether V and W are ranked highly. For example,
do they show up as one of the three strongest for that reading?)


API (See documentation on website)
----------------------------------

    curl -k -X POST -H "Content-Type:application/json"  -i http://localhost:6540/rssi_readings   -d '{"badge_id":"1", "pi_id":"2", "beacons":{"a": -30, "b": -35, "c": -40} }'


    curl -k -X POST -H "Content-Type:application/json"  -i http://localhost:6540/badges/2/location  -d '{"badge_id":"1", "pi_id":"2", "beacons":{"a": -30, "b": -35, "c": -40} }'


Bayes Priors and BASE RATE
--------------------------

Initially I thought this was a class-balanced classification problem.
However, let's think about the base rate in terms of David x.
Most of the time, a resident will be in their suite. (That's the base rate.)
So in light of new information from a location sensor (information that is
only somewhat reliable), it makes sense to use a Bayes xxx (classifier?)
to add that information in.

Example:
  * Judy is in her room 90% of the time (The base rate).
  * Our sensor says she is in her room (Classify: her suite)
  * Our sensor predicts equal likelihood of her being in her room
    vs her being in the room next to hers. (Classify: her suite)
  * Our sensor predicts that it's twice as likely that she's in the
    kitchen than in her suite (Now this is a tough call. How often is she
    actually in the kitchen?)



Making Database Backups of Training Runs and Associated Rssi Readings
---------------------------------------------------------------------

    cd /path/to/stethoscope
    env/bin/python stethoscope/scripts/backup_relevant_parts_of_database.py <output_file>

The parts of the database that we want to make sure we keep
are the training runs and the associated rssi readings.
All the other rssi readings could be thrown away and we
wouldn't care.

If you want to know where a resident was over the course of a year,
you would want to store location CHANGES so you're not saving so much data.



Restoring From a Database Backup
--------------------------------

    rm stethoscope.sqlite
    cat backups/<filename> | sqlite3 stethoscope.sqlite



BACKLOG
-------

  * Find out where timezone is set for database
    - at one point new readings were showing up as "7 hours ago"
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



