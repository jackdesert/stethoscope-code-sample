from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError
from sqlalchemy import desc

from ..models.util import PiTracker
from ..models.util import BadgeTracker
from ..models import RssiReading
from ..models import TrainingRun

from datetime import datetime

import ipdb
import json
import operator


#@view_config(route_name='test', renderer='json')
#def test_view(request):
#    # This view is only here to easily test model code with an dbsession
#    data, labels = TrainingRun.data_and_labels(request.dbsession)
#    return dict(data=data.tolist(), labels=labels.tolist())




@view_config(route_name='rssi_readings',
             renderer='../templates/rssi_readings.jinja2')
def rssi_readings_view(request):
    readings = request.dbsession.query(RssiReading).order_by(desc('id')).limit(50)
    return dict(readings=readings, now=datetime.now(), round=round)





@view_config(route_name='create_rssi_reading',
             renderer='json')
def create_rssi_reading_view(request):
    try:
        params = json.loads(request.body)
    except json.decoder.JSONDecodeError:
        request.response.status_code = 400
        return dict(errors='JSONDecodeError', payload_received=request.body.decode())

    reading = RssiReading(**rssi_reading_params(params))

    duplicate = reading.duplicate
    track_badge(params, duplicate)
    track_pi(params)

    if reading.invalid:
        request.response.status_code = 400
        return dict(errors=reading.errors)
    elif duplicate:
        request.response.status_code = 409
        return dict(errors=['duplicate'])
    else:
        request.response.status_code = 201
        request.dbsession.add(reading)
        return reading.to_dict()

def rssi_reading_params(params):
    whitelist = {'badge_id', 'badge_strength', 'pi_id', 'opposite_badge_id', 'position', 'motion'}
    output = { k:v for k,v in params.items() if k in whitelist }

    counter = 1
    beacons = params.get('beacons') or {}

    # Strength of -128 indicates no beacon heard; Ignore these.
    # Strength of None probably means malformed payload
    beacons = { k:v for (k,v) in beacons.items() if (v != None) and (v != RssiReading.NULL_BEACON_STRENGTH) }
    beacons_sorted = sorted(beacons.items(), key=operator.itemgetter(1), reverse=True)

    for beacon_id, beacon_strength in beacons_sorted:
        output[f'beacon_{counter}_id']       = beacon_id
        output[f'beacon_{counter}_strength'] = beacon_strength
        counter += 1
        if counter > 5:
            break
    return output


def track_pi(params):
    pi_id = params.get('pi_id')
    ip_address = params.get('ip_address')
    PiTracker.record(pi_id, ip_address)

def track_badge(params, duplicate):
    badge_id = params.get('badge_id')
    pi_id = params.get('pi_id')
    badge_strength = params.get('badge_strength')
    BadgeTracker.record(badge_id, badge_strength, pi_id, duplicate)




db_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_stethoscope_db" script
    to initialize your database tables.  Check your virtual
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""
