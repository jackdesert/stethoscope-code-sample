from pyramid.response import Response
from pyramid.view import view_config
import pdb


@view_config(route_name='docs__rssi_readings',
             renderer='doc/api/rssi_readings.md')

def landing_view(request):
    return {'one': 'one', 'project': 'stethoscope'}





