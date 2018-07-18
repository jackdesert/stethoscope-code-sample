from pyramid.response import Response
from pyramid.view import view_config
import pdb
from ..models.training_run import TrainingRun
from ..models.rssi_reading import RssiReading
from datetime import datetime
import json


@view_config(route_name='training_runs__index',
             renderer='../templates/training_runs__index.jinja2')
def training_runs(request):
    room_ids = [ id for (id,) in request.dbsession.query(TrainingRun.room_id).distinct().all() ]
    rooms = []

    for room_id in room_ids:
        total_readings = 0
        training_runs = request.dbsession.query(TrainingRun).filter_by(room_id=room_id).all()
        for t_run in training_runs:
            total_readings += len(t_run.rssi_readings)
        room = dict(id=room_id, training_runs=training_runs, total_readings=total_readings)
        rooms.append(room)

    return dict(rooms=rooms)



@view_config(route_name='training_runs__new',
             renderer='../templates/training_runs__new.jinja2')
def training_runs__new(request):
    room_ids = ['abc', 'def']
    badge_ids = [ id for (id,) in request.dbsession.query(RssiReading.badge_id).distinct().all() ]

    return dict(room_ids=room_ids, badge_ids=badge_ids)



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




@view_config(route_name='training_runs__bulk_stats',
             renderer='json')
def training_runs__bulk_stats_view(request):
    params = json.loads(request.body)
    training_run_ids = params.get('training_run_ids')
    room_id = params.get('room_id')

    if not training_run_ids:
        request.response.status_code = 400
        return {'error': 'Please supply training_run_ids'}
    if not room_id:
        request.response.status_code = 400
        return {'error': 'Please supply room_id'}

    output = { 'in_progress' : {},
               'completed' : 0,
               'total' : 0 }

    in_progress_training_runs = request.dbsession.query(TrainingRun). \
                    filter(TrainingRun.id.in_(training_run_ids))
    for t_run in in_progress_training_runs:
        if t_run.end_timestamp:
            request.response.status_code = 400
            return {'error': f'Training run with id {t_run.id} has already ended'}
        count = count_from_training_run(request.dbsession, t_run)
        output['in_progress'][t_run.badge_id] = count
        output['total'] += count

    completed_training_runs = request.dbsession.query(TrainingRun). \
                    filter_by(room_id=room_id). \
                    filter(TrainingRun.end_timestamp.isnot(None))

    for t_run in completed_training_runs:
        count = count_from_training_run(request.dbsession, t_run)
        output['completed'] += count
        output['total'] += count

    return output

def count_from_training_run(session, training_run):
    # TODO Move logic to model (How do you do that, since you need the session
    #                           to run queries?)
    qq = session.query(RssiReading). \
                    filter_by(badge_id=training_run.badge_id). \
                    filter(RssiReading.timestamp > training_run.start_timestamp)

    if training_run.end_timestamp:
        qq = qq.filter(RssiReading.timestamp < training_run.end_timestamp)

    return qq.count()

