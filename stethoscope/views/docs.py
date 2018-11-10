from pyramid.response import Response
from pyramid.view import view_config
import ipdb


@view_config(route_name='docs__rssi_readings',
             renderer='doc/api/rssi_readings.md')

def api_docs_rssi_readings_view(request):
    return {'one': 'one', 'project': 'stethoscope'}




@view_config(route_name='docs__location',
             renderer='doc/api/location.md')

def api_docs_location_view(request):
    return {'one': 'one', 'project': 'stethoscope'}




@view_config(route_name='docs__location_history',
             renderer='doc/api/location_history.md')

def api_docs_location_history_view(request):
    return {'one': 'one', 'project': 'stethoscope'}


