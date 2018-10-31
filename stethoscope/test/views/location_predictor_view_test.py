from pyramid import testing

import datetime
import pdb
import transaction
import unittest
import json

from stethoscope.test.base_test import BaseTest
from stethoscope.views.location import location_view

from stethoscope.models.neural_network import NeuralNetwork
from stethoscope.models.rssi_reading import RssiReading

def dummy_request(dbsession):
    return testing.DummyRequest(dbsession=dbsession)



############  RssiReadings View Tests Written by Jack  #########################

class TestLocationPredictorView(BaseTest):

    def setUp(self):
        super(TestLocationPredictorView, self).setUp()
        self.init_database()


        #model = MyModel(name='one', value=55)
        #self.session.add(model)

    def metadata(self):
        return NeuralNetwork.saved_metadata()

    def reading(self):
        # Use valid beacon ids from training set
        # Unfortunately, this means you have to have metadata
        # saved to disk before these tests will pass
        beacon_id_to_beacon_index = self.metadata().beacon_id_to_beacon_index
        beacon_ids = [bid for bid, _ in beacon_id_to_beacon_index.items()]
        return RssiReading(badge_id='2',
                           pi_id='1',
                           beacon_1_id=beacon_ids[0],
                           beacon_1_strength=-50)


    def test_no_readings_for_badge(self):

        req = dummy_request(self.session)
        req.matchdict['badge_id'] = '2'
        info = location_view(req)

        self.assertEqual(404, req.response.status_code)

        self.assertEqual(info, {'error': 'No RssiReadings received from badge 2 in last 60 seconds'})

    def test_happy_path_no_priors(self):
        reading = self.reading()
        self.session.add(reading)

        req = dummy_request(self.session)
        req.matchdict['badge_id'] = '2'

        #req.body = json.dumps(self.params_funky_beacons())
        info = location_view(req)
        self.assertTrue('raw' in info)
        self.assertTrue('bayes' not in info)

    def test_happy_path_with_priors(self):
        reading = self.reading()
        self.session.add(reading)

        req = dummy_request(self.session)
        req.matchdict['badge_id'] = '2'

        req.body = json.dumps(dict(priors=[['a', 5]]))
        info = location_view(req)
        self.assertTrue('raw' in info)
        self.assertTrue('bayes' in info)

    def test_all_beacons_imposters(self):
        reading = self.reading()
        reading.beacon_1_id = 'unknown-beacon'

        self.session.add(reading)

        req = dummy_request(self.session)
        req.matchdict['badge_id'] = '2'

        info = location_view(req)
        self.assertEqual(409, req.response.status_code)
        self.assertTrue('NoMatchingBeaconsError' in info['error'])

