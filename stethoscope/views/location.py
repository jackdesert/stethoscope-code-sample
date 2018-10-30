from pyramid.view import view_config
from ..models.util import PiTracker
from ..models.util import bip_rooms
from ..models.rssi_reading import RssiReading
from ..models.neural_network import NeuralNetwork
from ..models.neural_network_helper import NeuralNetworkHelper
from ..models.neural_network_helper import NoMatchingBeaconsError

from collections import defaultdict
from copy import deepcopy
from keras import backend as keras_backend
from keras import models
import json
import operator
import pdb
import pickle
import numpy as np


# Inflate Keras model outside the method so it doesn't get called during a request
model = models.load_model(NeuralNetwork.MODEL_FILEPATH)

# Call _make_predict_function to avoid getting error:
#   "*** ValueError: Tensor is not an element of this graph."
# see https://github.com/keras-team/keras/issues/6462#issuecomment-319232504
model._make_predict_function()
bip_rooms_memoized = bip_rooms()


# Predict which room is most likely based on the last RssiReading.
# TODO Update to use the last several RssiReadings and return the most common answer
# TODO move this code to a model
# Accepts priors and uses them in Bayesian fashion
@view_config(route_name='location',
             renderer='json')
def location_view(request):
    badge_id = request.matchdict.get('badge_id')
    if not badge_id in RssiReading.recent_badge_ids(request.dbsession):
        request.response.status_code = 404
        return dict(error=f'No RssiReadings received from badge {badge_id} in last {RssiReading.RECENT_SECONDS} seconds')


    reading = RssiReading.most_recent_from_badge(request.dbsession, badge_id)

    metadata = pickle.load(open(NeuralNetwork.METADATA_FILEPATH, 'rb'))
    try:
        reading_vectorized, imposter_beacons = NeuralNetworkHelper.vectorize_and_normalize_reading(reading, metadata)
    except NoMatchingBeaconsError:
        request.response.status_code = 409
        return dict(error=f'No Matching Beacons in RssiReading with id {reading.id} and beacons {reading.beacons}. This means that beacons used for training and beacons in this reading are disjoint.')

    # Nest it one deep so shape matches correctly
    reading_vectorized_2d = np.array([reading_vectorized])
    prediction = model.predict(reading_vectorized_2d)

    # TODO Cache bip_rooms to reduce network calls
    current_room_names_by_id = { rid: rname for (rid, rname) in bip_rooms_memoized }
    room_ids = metadata.room_ids



    raw = []
    for room_id, raw_probability in zip(room_ids, prediction[0]):
        room_name = current_room_names_by_id.get(room_id) or 'unknown'

        row = [room_id, float(raw_probability), room_name]
        raw.append(row)

    output = dict(raw=raw)


    if request.body:
        priors = json.loads(request.body).get('priors')
        priors_dict = {room_id: weight for room_id, weight in priors}

        total_weight = 0.0
        weights = {}

        for room_id in room_ids:
            # Default weight
            weight = priors_dict.get(room_id) or 1.0
            total_weight += weight
            weights[room_id] = weight

        bayes_weights_dict = {rid: weight/total_weight for rid, weight in weights.items()}

        bayes_before_normalization = []
        for room_id, raw_probability, room_name in raw:

            bayes_weight = bayes_weights_dict[room_id]
            bayes_probability = raw_probability * bayes_weight
            row = [room_id, bayes_probability, room_name, bayes_weight]
            bayes_before_normalization.append(row)

        bayes_total_probability = sum([bp for _, bp, _, _ in bayes_before_normalization])
        bayes = [[ri, bp / bayes_total_probability, rn, bw] for ri, bp, rn, bw in bayes_before_normalization]

        output['bayes'] = bayes



    for algorithm, data in output.items():
        # Sort by probability
        data.sort(key=operator.itemgetter(1), reverse=True)


    # Include information about the reading
    output['reading'] = dict(id                = reading.id,
                             pi_id             = reading.pi_id,
                             badge_id          = reading.badge_id,
                             beacons           = reading.beacons,
                             vectorized        = [float(i) for i in reading_vectorized],
                             timestamp         = str(reading.timestamp),
                             imposter_beacons  = list(imposter_beacons),)

    return output
