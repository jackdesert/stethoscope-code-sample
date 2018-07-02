from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from ..models import MyModel
from ..models import RssiReading

import pdb
import json
import operator


@view_config(route_name='home', renderer='../templates/mytemplate.jinja2')
def my_view(request):
    try:
        query = request.dbsession.query(MyModel)
        one = query.filter(MyModel.name == 'one').first()
    except DBAPIError:
        return Response(db_err_msg, content_type='text/plain', status=500)
    return {'one': one, 'project': 'stethoscope'}


@view_config(route_name='create_rssi_reading',
             renderer='json',
             request_method='POST')
def haberdasher(request):
    reading = RssiReading(**rssi_reading_params(request))
    if reading.invalid:
        request.response.status_code = 400
        return dict(errors=reading.errors)
    elif reading.duplicate:
        request.response.status_code = 409
        return dict(errors=['duplicate'])
    else:
        request.response.status_code = 201
        request.dbsession.add(reading)
        return reading.to_dict()

def rssi_reading_params(request):
    whitelist = {'badge_id', 'pi_id'}
    params = json.loads(request.body)
    output = { k:v for k,v in params.items() if k in whitelist }

    counter = 1
    beacons = params.get('beacons') or {}
    for beacon_id, beacon_strength in sorted(beacons.items(), key=operator.itemgetter(0)):
        output[f'beacon_{counter}_id']       = beacon_id
        output[f'beacon_{counter}_strength'] = beacon_strength
        counter += 1
        if counter > 3:
            break
    return output






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
