from pyramid import testing

from datetime import timedelta
from datetime import datetime
import pdb
import transaction
import unittest

from stethoscope.test.base_test import BaseTest
from stethoscope.models.training_run import TrainingRun
from stethoscope.models.rssi_reading import RssiReading



############ TrainingRun Model Tests Written by Jack  #########################

class TestTrainingRun(BaseTest):

    def setUp(self):
        super(TestTrainingRun, self).setUp()
        self.init_database()


    def validTrainingRun(self):
        now = datetime.now()
        one_hour_ago = now - timedelta(seconds=3600)


        training_run = TrainingRun(room_id='a',
                                   badge_id='b',
                                   start_timestamp=one_hour_ago,
                                   end_timestamp=now)
        return training_run

    def matchingRssiReading(self, timestamp):
        rr = RssiReading(timestamp=timestamp,
                         badge_id='b',
                         pi_id='c',
                         badge_strength=-70,
                         beacon_1_id='d',
                         beacon_1_strength=-60)
        return rr



    def test_happy_path(self):
        trun = self.validTrainingRun()
        self.assertTrue(trun.valid)

    def test_fails_del_no_badge_id(self):
        trun = self.validTrainingRun()
        trun.badge_id = None
        self.assertFalse(trun.valid)
        self.assertTrue(trun.invalid)

    def test_fails_del_no_room_id(self):
        trun = self.validTrainingRun()
        trun.room_id = None
        self.assertFalse(trun.valid)
        self.assertTrue(trun.invalid)


    def test_rssi_readings_happy_path(self):
        trun = self.validTrainingRun()
        reading_1 = self.matchingRssiReading(trun.end_timestamp - timedelta(seconds=10))
        reading_2 = self.matchingRssiReading(trun.end_timestamp - timedelta(seconds=20))

        reading_3_other_badge = self.matchingRssiReading(trun.end_timestamp - timedelta(seconds=30))
        reading_3_other_badge.badge_id = 'something-else'

        reading_4_no_beacons = self.matchingRssiReading(trun.end_timestamp - timedelta(seconds=40))
        reading_4_no_beacons.beacon_1_id = None
        reading_4_no_beacons.beacon_1_strength = None

        self.session.add(trun)
        self.session.add(reading_1)
        self.session.add(reading_2)
        self.session.add(reading_3_other_badge)
        self.session.add(reading_4_no_beacons)

        self.session.flush()
        expected_ids = {reading_1.id, reading_2.id}
        ids = {rr.id for rr in trun.rssi_readings(self.session, True)}

        self.assertEqual(ids, expected_ids)

    def test_rssi_reading_ids_from_all_completed_training_runs(self):

        trun_1 = self.validTrainingRun()
        reading_1 = self.matchingRssiReading(trun_1.end_timestamp - timedelta(seconds=10))

        trun_2 = self.validTrainingRun()
        trun_2.start_timestamp = datetime.now() - timedelta(days=1)
        trun_2.end_timestamp = trun_2.start_timestamp + timedelta(seconds=3600)
        reading_2 = self.matchingRssiReading(trun_2.end_timestamp - timedelta(seconds=10))

        reading_2a_no_beacons = self.matchingRssiReading(trun_2.end_timestamp - timedelta(seconds=10))
        reading_2a_no_beacons.beacon_1_id = None
        reading_2a_no_beacons.beacon_1_strength = None

        trun_3_not_completed = self.validTrainingRun()
        trun_3_not_completed.start_timestamp = datetime.now() - timedelta(days=2)
        trun_3_not_completed.end_timestamp = None
        reading_3 = self.matchingRssiReading(trun_3_not_completed.start_timestamp + timedelta(seconds=1))

        self.session.add(trun_1)
        self.session.add(reading_1)
        self.session.add(trun_2)
        self.session.add(reading_2)
        self.session.add(reading_2a_no_beacons)
        self.session.add(trun_3_not_completed)
        self.session.add(reading_3)

        self.session.flush()


        expected_ids = {reading_1.id, reading_2.id}
        ids = {id for id in TrainingRun.rssi_reading_ids_from_all_completed_training_runs(self.session)}

        self.assertEqual(ids, expected_ids)
