from pyramid.view import view_config
from ..models.util import PiTracker
from ..models.util import bip_rooms
from ..models.rssi_reading import RssiReading
from ..models.neural_network import NeuralNetwork
from ..models.neural_network_helper import NeuralNetworkHelper
from ..models.neural_network_helper import NoMatchingBeaconsError
from ..models.location_predictor import LocationPredictor

from collections import defaultdict
from copy import deepcopy
from keras import backend as keras_backend
from keras import models
import json
import operator
import ipdb
import pickle
import numpy as np


# Predict which room is most likely based on the last RssiReading.
# TODO Update to use the last several RssiReadings and return the most common answer
# Accepts priors and uses them in Bayesian fashion
@view_config(route_name='location',
             renderer='json')
def location_view(request):
    badge_id = request.matchdict.get('badge_id')
    if not badge_id in RssiReading.recent_badge_ids(request.dbsession):
        request.response.status_code = 404
        return dict(error=f'No RssiReadings received from badge {badge_id} in last {RssiReading.RECENT_SECONDS} seconds')


    reading = RssiReading.most_recent_from_badge(request.dbsession, badge_id)

    priors = None
    if request.body:
        priors = json.loads(request.body).get('priors')

    predictor = LocationPredictor(reading, priors=priors)

    try:
        output = predictor.location
    except NoMatchingBeaconsError as ee:
        request.response.status_code = 409
        msg = ee.__repr__()
        output = dict(error=msg)

    if 'reading' in output:
        count = RssiReading.recent_count_for_badge(request.dbsession, badge_id, 600)
        output['reading']['num_readings_last_10_min'] = count

    return output




