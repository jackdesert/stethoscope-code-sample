from pyramid.response import Response
from pyramid.view import view_config
import pdb


@view_config(route_name='landing', renderer='../templates/landing.jinja2')
def landing_view(request):
    return {'one': 'one', 'project': 'stethoscope'}




