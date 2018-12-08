from ..models import NeuralNetwork
from ..models import NeuralNetworkHelper
from ..models.util import bip_rooms_hash as bip_rooms_hash_callable
from ..models.util import PiName

from keras import models
import numpy as np
import operator
import ipdb
import pickle

class LocationPredictor:

    # This model will fail to load if these files not available
    KERAS_MODEL    = NeuralNetwork.saved_model()
    KERAS_METADATA = NeuralNetwork.saved_metadata()
    BIP_ROOMS_HASH = bip_rooms_hash_callable()

    DEFAULT_BAYES_WEIGHT = 1.0
    UNKNOWN_ROOM = 'unknown'

    # Pass in keras_model and keras_metadata when running tests
    def __init__(self, rssi_reading,
                       priors=None,
                       bip_rooms_hash=BIP_ROOMS_HASH,
                       keras_model=KERAS_MODEL,
                       keras_metadata=KERAS_METADATA):

        self.priors = priors
        self.reading = rssi_reading
        self.keras_model = keras_model
        self.keras_metadata = keras_metadata
        self.keras_room_ids = keras_metadata.room_ids
        self.bip_rooms_hash = bip_rooms_hash

    @property
    def location(self):
        self._compute_raw()
        self._compute_bayes()

        output = dict(raw=self.raw)

        if self.bayes:
            output['bayes'] = self.bayes

        # Include information about the reading
        output['reading'] = dict(id                = self.reading.id,
                                 first_pi_id       = self.reading.pi_id,
                                 first_pi_name     = PiName.by_id(self.reading.pi_id),
                                 first_pi_badge_strength    = self.reading.badge_strength,
                                 badge_id          = self.reading.badge_id,
                                 # placeholder to preserver order (see view)
                                 num_readings_last_10_min = None,
                                 beacons           = self.reading.beacons,
                                 vectorized        = [float(i) for i in self.reading_vectorized],
                                 timestamp         = str(self.reading.timestamp),
                                 opposite_badge_id = self.reading.opposite_badge_id,
                                 position          = self.reading.position,
                                 motion            = self.reading.motion,
                                 imposter_beacons  = list(self.imposter_beacons),)

        return output


    def _keras_prediction(self):
        self.reading_vectorized, self.imposter_beacons = NeuralNetworkHelper.vectorize_and_normalize_reading(self.reading, self.keras_metadata)


        # Nest it one deep so shape matches correctly
        reading_vectorized_2d = np.array([self.reading_vectorized])
        prediction = self.keras_model.predict(reading_vectorized_2d)
        return prediction


    def _compute_raw(self):
        prediction = self._keras_prediction()
        raw = []

        for room_id, raw_probability in zip(self.keras_room_ids, prediction[0]):
            room_name = self.bip_rooms_hash.get(room_id) or self.UNKNOWN_ROOM

            row = [room_id, float(raw_probability), room_name]
            raw.append(row)

        self._sort_by_probability(raw)
        self.raw = raw


    def _compute_bayes(self):
        if not self.priors:
            self.bayes = None
            return

        priors_dict = {room_id: weight for room_id, weight in self.priors}

        total_weight = 0.0
        weights = {}

        for room_id in self.keras_room_ids:
            # Default weight
            weight = priors_dict.get(room_id) or self.DEFAULT_BAYES_WEIGHT
            total_weight += weight
            weights[room_id] = weight

        bayes_weights_dict = {rid: weight/total_weight for rid, weight in weights.items()}

        bayes_before_normalization = []
        for room_id, raw_probability, room_name in self.raw:

            bayes_weight = bayes_weights_dict[room_id]
            bayes_probability = raw_probability * bayes_weight
            row = [room_id, bayes_probability, room_name, bayes_weight]
            bayes_before_normalization.append(row)

        bayes_total_probability = sum([bp for _, bp, _, _ in bayes_before_normalization])

        # Normalize so they add up to 1.0
        bayes = [[ri, bp / bayes_total_probability, rn, bw] for ri, bp, rn, bw in bayes_before_normalization]

        self._sort_by_probability(bayes)
        self.bayes = bayes

    def _sort_by_probability(self, items):
        items.sort(key=operator.itemgetter(1), reverse=True)


