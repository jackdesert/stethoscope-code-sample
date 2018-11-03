from ..models import NeuralNetwork
from ..models import NeuralNetworkHelper
from ..models.util import bip_rooms_hash

from keras import models
import numpy as np
import operator
import pdb
import pickle

class LocationPredictor:

    # This model will fail to load if these files not available
    KERAS_MODEL    = NeuralNetwork.saved_model()
    KERAS_METADATA = NeuralNetwork.saved_metadata()
    BIP_ROOMS_HASH = bip_rooms_hash()

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
                                 pi_id             = self.reading.pi_id,
                                 badge_id          = self.reading.badge_id,
                                 beacons           = self.reading.beacons,
                                 vectorized        = [float(i) for i in self.reading_vectorized],
                                 timestamp         = str(self.reading.timestamp),
                                 opposite_badge_id = self.reading.opposite_badge_id,
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


