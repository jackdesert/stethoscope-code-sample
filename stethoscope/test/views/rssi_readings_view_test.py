from pyramid import testing

import datetime
import pdb
import transaction
import unittest

from stethoscope.test.base_test import BaseTest

def dummy_request(dbsession):
    return testing.DummyRequest(dbsession=dbsession)



############  RssiReadings View Tests Written by Jack  #########################

class TestRssiReadingsView(BaseTest):

    def setUp(self):
        super(TestRssiReadingsView, self).setUp()
        self.init_database()


        #model = MyModel(name='one', value=55)
        #self.session.add(model)

    def params(self):
        # Instantiating out of order to make sure
        # it is sorting *by value*
        return dict(badge_id='badge_0',
                    pi_id='pi_0',
                    beacons=dict(a=10, b=30, d=20, e=40, c=50, f=0))

    def params_funky_beacons(self):
        return dict(badge_id='badge_0',
                    pi_id='pi_0',
                    beacons=dict(a=10, b=None))

    def test_funky_beacons(self):
        from stethoscope.views.rssi_readings import create_rssi_reading_view
        import json

        req = dummy_request(self.session)
        req.body = json.dumps(self.params_funky_beacons())
        info = create_rssi_reading_view(req)
        self.assertEqual(info, {'badge_id': 'badge_0',
                                'pi_id': 'pi_0',
                                'beacon_1_id': 'a',
                                'beacon_1_strength': 10 },
                          'Drops beacon "b" entirely')

    def test_ordered_beacons(self):
        from stethoscope.views.rssi_readings import create_rssi_reading_view
        import json

        req = dummy_request(self.session)
        req.body = json.dumps(self.params())
        info = create_rssi_reading_view(req)
        self.assertEqual(info, {'badge_id': 'badge_0',
                                'pi_id': 'pi_0',
                                'beacon_1_id': 'c',
                                'beacon_2_id': 'e',
                                'beacon_3_id': 'b',
                                'beacon_4_id': 'd',
                                'beacon_5_id': 'a',
                                'beacon_1_strength': 50,
                                'beacon_2_strength': 40,
                                'beacon_3_strength': 30,
                                'beacon_4_strength': 20,
                                'beacon_5_strength': 10},
                          'Returns 5 of 6 in sorted order')

    def test_ordered_beacons_only_two(self):
        from stethoscope.views.rssi_readings import create_rssi_reading_view
        import json

        req = dummy_request(self.session)
        params = self.params()
        del params['beacons']['c']
        del params['beacons']['e']
        del params['beacons']['a']
        del params['beacons']['f']
        req.body = json.dumps(params)
        info = create_rssi_reading_view(req)
        self.assertEqual(info, {'badge_id': 'badge_0',
                                'pi_id': 'pi_0',
                                'beacon_1_id': 'b',
                                'beacon_2_id': 'd',
                                'beacon_1_strength': 30,
                                'beacon_2_strength': 20},
                          'Returns 2 in sorted order')

    def test_malformed_json(self):
        from stethoscope.views.rssi_readings import create_rssi_reading_view
        import json

        req = dummy_request(self.session)
        req.body = '{malformed json'.encode()
        create_rssi_reading_view(req)
        self.assertEqual(req.response.status_code, 400, 'Returns status code 400')

#class TestMyViewFailureCondition(BaseTest):
#
#    def test_failing_view(self):
#        from stethoscope.views.rssi_readings import my_view
#        info = my_view(dummy_request(self.session))
#        self.assertEqual(info.status_int, 500)
#                    beacon_1_id='x',
#                    beacon_2_id='y',
#                    beacon_3_id='z',
#                    beacon_1_strength=10,
#                    beacon_2_strength=20,
#                    beacon_3_strength=30)

