from pyramid.view import view_config
import pdb
from ..models.util import PiTracker

@view_config(route_name='ansible', renderer='string')
def ansible_view(request):
    pis = ['# /etc/ansible/hosts']
    for pi in PiTracker.pis():
        # Omit pis without leading zeros, because they are from tools/throw
        if '0000' in pi:
            pis.append(pi)

    return '\n'.join(pis)


