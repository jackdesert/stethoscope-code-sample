from pyramid.response import Response
from pyramid.view import view_config

#from sqlalchemy.exc import DBAPIError
from sqlalchemy import desc

#from ..models import MyModel
from ..models import RssiReading

from datetime import datetime

import pdb
#import json
#import operator




@view_config(route_name='badge_show',
             renderer='../templates/badge.jinja2')
def badge_smoothie(request):
    id = request.matchdict['id']
    last_reading_for_badge = request.dbsession.query(RssiReading).filter_by(badge_id=id).order_by(desc('id')).limit(1).all()[0]

    output = { 'id'          : id,
               'server_time' : str(datetime.now()),
               'max_id'      : last_reading_for_badge.id }

    return output



@view_config(route_name='badge_fetch',
             renderer='json')
def badge_fetch_timeseries(request):

    id = request.matchdict['id']
    packets = []
    readings = request.dbsession.query(RssiReading).filter_by(badge_id=id)
    if 'after' in request.params:
        after = int(request.params['after'])
        readings = readings.filter(RssiReading.id > after)
    readings = readings.limit(1)
    for rr in readings:
        beacons = {rr.beacon_1_id : rr.beacon_1_strength,
                   rr.beacon_2_id : rr.beacon_2_strength,
                   rr.beacon_3_id : rr.beacon_3_strength}
        packet = dict(id=rr.id, timestamp=str(rr.timestamp), beacons=beacons)
        packets.append(packet)


    return packets

