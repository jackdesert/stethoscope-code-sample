from pyramid import testing

import datetime
import ipdb
import transaction
import pytest
import unittest
import numpy as np
from unittest.mock import patch
from collections import namedtuple
from stethoscope.test.base_test import BaseTest
from stethoscope.models.rssi_reading import RssiReading
from stethoscope.models.location_predictor import LocationPredictor
from stethoscope.models.neural_network_helper import NoMatchingBeaconsError

# TODO Find a way to not have to paste this both here and in models/training_run.py
KerasMetadata = namedtuple('KerasMetadata', ['room_ids', 'beacon_id_to_beacon_index', 'strength_range', 'min_strength'])


class TestLocationPredictor(BaseTest):

#    def setUp(self):
#        # Flush Redis before each test
#        super(TestRssiReadingDuplicate, self).setUp()
#        from stethoscope.models.rssi_reading import RssiReading
#        redis = RssiReading.REDIS
#        redis.flushall()

    def reading(self):
        return RssiReading(badge_id='a',
                           pi_id='b',
                           beacon_1_id='x',
                           beacon_2_id='y',
                           beacon_3_id='z',
                           beacon_1_strength=10,
                           beacon_2_strength=20,
                           beacon_3_strength=30,
                           opposite_badge_id='c',
                           position=2,
                           motion=3)


    def metadata(self):
        room_ids = ['a', 'b']
        beacon_id_to_beacon_index = {'x': 0, 'y': 1, 'z': 2}
        strength_range = 30
        min_strength = -70
        mm = KerasMetadata(room_ids,
                           beacon_id_to_beacon_index,
                           strength_range,
                           min_strength)
        return mm



    @patch('keras.models.Model')
    def test_location_happy_path_no_priors(self, MockModel):
        rr = self.reading()
        mock_model = MockModel()
        mock_model.predict.return_value = [[0.3, 0.7]]
        predictor = LocationPredictor(rr,
                                      keras_model = mock_model,
                                      keras_metadata = self.metadata(),
                                      bip_rooms_hash = dict(a='Room A', b='Room B'))
        location = predictor.location


        raw = location['raw']

        # total probabilities sum to 1.0
        total_raw_probability = sum([rp for (_, rp, _) in raw])
        self.assertEqual(total_raw_probability, 1.0)

        # Note these come back ordered by probability (second item)
        expected_raw = [['b', 0.7, 'Room B'], ['a', 0.3, 'Room A']]
        self.assertEqual(expected_raw, raw)

        self.assertTrue(predictor.bayes == None, 'No priors passed in so location.bayes is None')
        self.assertTrue(location.get('bayes') == None, 'No priors passed in so bayes in payload is None')

        expected_reading = {'id': None,
                            'pi_id': 'b',
                            'badge_id': 'a',
                            'beacons': [('x', 10), ('y', 20), ('z', 30)],
                            'vectorized': [2.6666666666666665, 3.0, 3.3333333333333335],
                            'timestamp': 'None',
                            'position': 2,
                            'motion': 3,
                            'opposite_badge_id': 'c',
                            'imposter_beacons': []}
        self.assertEqual(expected_reading, location['reading'])

    @patch('keras.models.Model')
    def test_location_happy_path_no_priors_no_bip_rooms_hash(self, MockModel):
        rr = self.reading()
        mock_model = MockModel()
        mock_model.predict.return_value = [[0.3, 0.7]]
        predictor = LocationPredictor(rr,
                                      keras_model = mock_model,
                                      keras_metadata = self.metadata())
        location = predictor.location


        # Rooms "a" and "b" are not real rooms, so they come back with name "unknown"
        raw = location['raw']
        room_names = [rn for (_,_,rn) in raw]
        self.assertEqual(set(room_names), {'unknown'})

    @patch('keras.models.Model')
    def test_location_happy_path_with_priors(self, MockModel):
        rr = self.reading()
        mock_model = MockModel()
        mock_model.predict.return_value = [[0.3, 0.7]]
        predictor = LocationPredictor(rr,
                                      keras_model = mock_model,
                                      keras_metadata = self.metadata(),
                                      bip_rooms_hash = dict(a='Room A', b='Room B'),
                                      priors = [['a', 5], ['unknown-room', 4]])
        location = predictor.location
        raw   = location['raw']
        bayes = location['bayes']

        # total probabilities sum to 1.0
        total_bayes_probability = sum([bp for (_, bp, _, _) in bayes])
        self.assertEqual(total_bayes_probability, 1.0)

        # total weights sum to 1.0
        total_weights = sum([w for (_,_,_,w) in bayes])
        self.assertEqual(total_weights, 1.0)

        # We passed in a (prior) weight of 5 of room "a".
        # We expect room "b" to get the default weight of 1.0
        # We test this by making sure the weight returned for "a" is 5x as big as for "b"
        weights = [w for (_,_,_,w) in bayes]

        # Floating points are not exact, so using numpy.isclose to compare
        self.assertTrue(np.isclose(weights[0], 5 * weights[1]))

        # Seems redundant to verify things above AND verify the exact
        # response here. But the things above will check math errors,
        # and this copypasta will check if things change visibly.
        expected_bayes = [['a', 0.6818181818181819, 'Room A', 0.8333333333333334],
                          ['b', 0.3181818181818182, 'Room B', 0.16666666666666666]]
        self.assertEqual(expected_bayes, bayes)


    @patch('keras.models.Model')
    def test_location_one_imposter_beacon(self, MockModel):
        rr = self.reading()
        rr.beacon_1_id = 'unknown-beacon'

        mock_model = MockModel()
        mock_model.predict.return_value = [[0.3, 0.7]]
        predictor = LocationPredictor(rr,
                                      keras_model = mock_model,
                                      keras_metadata = self.metadata())
        location = predictor.location

        expected = ['unknown-beacon']
        self.assertEqual(expected, location['reading']['imposter_beacons'])

    @patch('keras.models.Model')
    def test_location_all_imposter_beacons(self, MockModel):
        rr = self.reading()
        rr.beacon_1_id = 'unknown-beacon-1'
        rr.beacon_2_id = 'unknown-beacon-2'
        rr.beacon_3_id = 'unknown-beacon-3'

        mock_model = MockModel()
        mock_model.predict.return_value = [[0.3, 0.7]]
        predictor = LocationPredictor(rr,
                                      keras_model = mock_model,
                                      keras_metadata = self.metadata())

        with pytest.raises(NoMatchingBeaconsError):
            predictor.location



