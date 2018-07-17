from pyramid.response import Response
from pyramid.view import view_config
import pdb
from ..models.training_run import TrainingRun
from datetime import datetime
import json




@view_config(route_name='training_runs__bulk_start',
             renderer='json')
def training_runs__bulk_start_view(request):
    params = json.loads(request.body)
    room_id  = params.get('room_id')
    badge_ids = params.get('badge_ids')
    if not room_id:
        request.response.status_code = 400
        return {'error': 'Please supply room_id'}
    if not badge_ids:
        request.response.status_code = 400
        return {'error': 'Please supply badge_ids'}

    ids = []
    # Manually set start_timestamp so they are synchronized
    now = datetime.now()
    for badge_id in badge_ids:
        t_run = TrainingRun(room_id=room_id,
                            badge_id=badge_id,
                            start_timestamp=now)
        request.dbsession.add(t_run)
        request.dbsession.flush()
        ids.append(t_run.id)

    request.response.status_code = 201
    return dict(training_run_ids=ids)


# Curl Example
# curl -X POST -H "Content-Type:application/json"  -i http://localhost:6540/training_runs/bulk_start  -d '{"room_id":"room_a", "badge_ids":["badge_1", "badge_2"]}'



@view_config(route_name='training_runs__bulk_end',
             renderer='json')
def training_runs__bulk_end_view(request):
    params = json.loads(request.body)
    training_run_ids = params.get('training_run_ids')

    if not training_run_ids:
        request.response.status_code = 400
        return {'error': 'Please supply training_run_ids'}

    training_runs = request.dbsession.query(TrainingRun). \
                    filter(TrainingRun.id.in_(training_run_ids)).all()

    # Manually set end_timestamp so they are synchronized
    now = datetime.now()
    for t_run in training_runs:
        if t_run.end_timestamp:
            request.response.status_code = 409
            return {'error': f'TrainingRun with id "{t_run.id}" has already ended'}
        t_run.end_timestamp = now
        request.dbsession.add(t_run)
    return None


# Curl Example
# curl -X POST -H "Content-Type:application/json"  -i http://localhost:6540/training_runs/bulk_end  -d '{"training_run_ids":[1,2]}'
