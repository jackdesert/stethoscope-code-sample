from pyramid.view import view_config
import ipdb
from ..models.util import PiTracker

@view_config(route_name='ansible', renderer='string')
def ansible_view(request):
    pis = ['# /etc/ansible/hosts',
           '#',
           '# Address         CPU       Last Seen']
    for pi in PiTracker.pis():
        # Omit pis without leading zeros, because they are from tools/throw
        zeros = '0' * 8
        if zeros in pi:
            pi = pi.replace(zeros, '')
            pis.append(pi)

    return '\n'.join(pis)


