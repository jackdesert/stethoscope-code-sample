from pyramid.view import view_config
from ..models.util import PiTracker
from ..models.util import bip_rooms
from ..models.rssi_reading import RssiReading
from collections import defaultdict
from copy import deepcopy
import operator
import json
import pdb



# For now, this endpoint is a stub.
# That is, it does not yet connect to the keras model to actually
# predict which room is most likely.
# However, it does accept the correct payload (priors)
# And does return some semblance of probability that is based on the
# priors you pass in.
@view_config(route_name='location',
             renderer='json')
def location_view(request):
    badge_id = request.matchdict.get('badge_id')
    if not badge_id in RssiReading.recent_badge_ids(request.dbsession):
        request.response.status_code = 404
        return dict(error=f'No RssiReadings received from badge {badge_id} in last {RssiReading.RECENT_SECONDS} seconds')

    rooms = bip_rooms()
    room_ids = {room_id for room_id, room_name in rooms}


    # Raw gets equal weighting
    room_count = len(rooms)
    raw_weights_dict = defaultdict(lambda: 1/room_count)

    raw = []
    for room_id, room_name in rooms:
        row = [room_id, raw_weights_dict[room_id], room_name]
        raw.append(row)

    output = dict(raw=raw)


    if request.body:
        priors = json.loads(request.body).get('priors')
        prior_room_ids = {room_id for room_id, weight in priors}

        if not room_ids.issuperset(prior_room_ids):
            request.response.status_code = 409
            return dict(error=f'The following prior room ids not found in bip rooms: { prior_room_ids - room_ids }')


        bayes_weights_dict = defaultdict(float)
        total_weight = sum([weight for _, weight in priors])
        for room_id, weight in priors:
            bayes_weights_dict[room_id] = weight / total_weight

        bayes = []
        for room_id, room_name in rooms:
            prior_probability = bayes_weights_dict[room_id]
            # Until we run the endpoint through keras, prior probability is
            # the only meaningful information we have. Therefore,
            # probability = prior_probability
            probability = prior_probability
            row = [room_id, probability, room_name, prior_probability]
            bayes.append(row)
        output['bayes'] = bayes

    for algorithm, data in output.items():
        # Sort by probability
        data.sort(key=operator.itemgetter(1), reverse=True)

    return output
