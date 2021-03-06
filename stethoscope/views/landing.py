from pyramid.response import Response
from pyramid.view import view_config
import ipdb
from ..models import RssiReading
from ..models.util import PiTracker
from datetime import datetime, timedelta








@view_config(route_name='landing', renderer='../templates/landing.jinja2')
def landing_view(request):
    n_seconds_ago = datetime.now() - timedelta(seconds=RssiReading.RECENT_SECONDS)
    badge_rows = request.dbsession.query(RssiReading.badge_id) \
                   .filter(RssiReading.timestamp > n_seconds_ago) \
                   .distinct(RssiReading.badge_id) \
                   .all()

    active_badge_ids = [badge_id for (badge_id,) in badge_rows]
    active_badge_ids.sort()

    active_pi_ids = PiTracker.active_pis()
    active_pi_ids.sort()




    return dict(active_badge_ids=active_badge_ids,
                active_pi_ids=active_pi_ids,
                project='stethoscope')


