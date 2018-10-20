from ..models.training_run import TrainingRun
from ..models.training_run import TrainingRunExpectedCompleteError
from ..models.rssi_reading import RssiReading
from ..models.util import bip_rooms

from collections import defaultdict
from datetime import datetime
from pyramid.response import Response
from pyramid.view import view_config

import json
import pdb


@view_config(route_name='training_runs__index',
             renderer='../templates/training_runs__index.jinja2')
def training_runs(request):
    rooms = []
    room_list = bip_rooms()
    completed_runs_dict = defaultdict(list)

    for tr in TrainingRun.completed(request.dbsession):
        completed_runs_dict[tr.room_id].append(tr)

    for room_id, room_name in room_list:
        cruns = completed_runs_dict[room_id]
        room_reading_count = 0
        for crun in cruns:
            # This will set crun.count_rssi_readings_memoized
            # so we can refer to it in the template
            count = crun.count_rssi_readings(request.dbsession, True)
            room_reading_count += count
        room = dict(id=room_id, name=room_name,
                    completed_runs=cruns, reading_count=room_reading_count)
        rooms.append(room)

    return dict(rooms=rooms)



@view_config(route_name='training_runs__new',
             renderer='../templates/training_runs__new.jinja2')
def training_runs__new(request):
    rooms = bip_rooms()
    badge_ids = RssiReading.recent_badge_ids(request.dbsession)

    return dict(rooms=rooms, badge_ids=badge_ids)



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
                    filter(TrainingRun.id.in_(training_run_ids))

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
               'in_progress_total' : 0,
               'completed' : 0,
               'total' : 0 }

    in_progress_training_runs = TrainingRun.with_ids(request.dbsession, training_run_ids)

    for t_run in in_progress_training_runs:
        try:
            count = t_run.count_rssi_readings(request.dbsession, False)
        except TrainingRunExpectedCompleteError:
            request.response.status_code = 409
            return {'error': f'Training run with id {t_run.id} has already ended'}
        output['in_progress'][t_run.badge_id] = count
        output['in_progress_total'] += count
        output['total'] += count

    completed_training_runs = TrainingRun.completed_for_room(request.dbsession, room_id)

    for t_run in completed_training_runs:
        count = t_run.count_rssi_readings(request.dbsession, True)
        output['completed'] += count
        output['total'] += count


    return output
