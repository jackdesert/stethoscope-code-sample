from pyramid import testing

import datetime
import ipdb
import transaction
import unittest
from stethoscope.test.base_test import BaseTest


############ RssiReading  Model Tests Written by Jack  #########################

class TestRssiReadingDuplicate(BaseTest):

    def setUp(self):
        # Flush Redis before each test
        super(TestRssiReadingDuplicate, self).setUp()
        from stethoscope.models.rssi_reading import RssiReading
        redis = RssiReading.REDIS
        redis.flushall()

    def reading(self):
        from stethoscope.models.rssi_reading import RssiReading

        reading = RssiReading(badge_id='a',
                              badge_strength=-70,
                              pi_id='b',
                              beacon_1_id='x',
                              beacon_2_id='y',
                              beacon_3_id='z',
                              beacon_1_strength=10,
                              beacon_2_strength=20,
                              beacon_3_strength=30)

        return reading

    def test_valid(self):
        rr = self.reading()
        self.assertTrue(rr.valid)

    def test_valid_no_badge_strength(self):
        rr = self.reading()
        rr.badge_strength = None
        self.assertFalse(rr.valid)

    def test_duplicate(self):
        rr = self.reading()
        self.assertFalse(rr.duplicate)

    def test_duplicate_twice(self):
        rr = self.reading()
        self.assertFalse(rr.duplicate, 'first time expected to be unique')
        self.assertTrue(rr.duplicate, 'second time expected to be duplicate')
        self.assertTrue(rr.duplicate, 'third time expected to be duplicate')
        self.assertTrue(rr.duplicate, 'fourth time expected to be duplicate')

    def test_with_literal_delays(self):
        import time
        first_delay = 5.4
        second_delay = 0.2

        rr = self.reading()
        self.assertFalse(rr.duplicate, 'first time expected to be unique')

        # TODO Find a way to test redis expiration without literal sleep
        time.sleep(first_delay)
        self.assertTrue(rr.duplicate, f'after {first_delay} seconds, expected dup')

        time.sleep(second_delay)
        self.assertFalse(rr.duplicate, f'after {first_delay+second_delay} seconds expected to be original')

    def test_multiple_times_with_different_payloads(self):
        rr = self.reading()
        self.assertFalse(rr.duplicate, 'first time expected to be unique')

        rr.pi_id = 'something-different'
        self.assertTrue(rr.duplicate, 'pi_id does not affect uniqueness')

        rr.badge_strength = -2
        self.assertTrue(rr.duplicate, 'badge_strength does not affect uniqueness')




        rr.badge_id += '-'
        self.assertFalse(rr.duplicate, 'expected unique del badge_id changed')

        rr.beacon_1_id += '-'
        self.assertFalse(rr.duplicate, 'expected unique del beacon_1_id changed')

        rr.beacon_2_id += '-'
        self.assertFalse(rr.duplicate, 'expected unique del beacon_2_id changed')

        rr.beacon_3_id += '-'
        self.assertFalse(rr.duplicate, 'expected unique del beacon_3_id changed')

        rr.beacon_4_id = 'BIP600'
        self.assertFalse(rr.duplicate, 'expected unique del beacon_4_id changed')

        rr.beacon_5_id = 'BIP600'
        self.assertFalse(rr.duplicate, 'expected unique del beacon_5_id changed')

        rr.beacon_1_strength += 1
        self.assertFalse(rr.duplicate, 'expected unique del beacon_1_strength changed')

        rr.beacon_2_strength += 1
        self.assertFalse(rr.duplicate, 'expected unique del beacon_2_strength changed')

        rr.beacon_3_strength += 1
        self.assertFalse(rr.duplicate, 'expected unique del beacon_3_strength changed')

        rr.beacon_4_strength = -100
        self.assertFalse(rr.duplicate, 'expected unique del beacon_4_strength changed')

        rr.beacon_5_strength = -100
        self.assertFalse(rr.duplicate, 'expected unique del beacon_5_strength changed')



class TestRssiReadingTimestampAgo(BaseTest):

    def reading_with_timestamp(self, seconds_ago):
        import datetime
        from stethoscope.models.rssi_reading import RssiReading
        now = datetime.datetime.now()
        delta = datetime.timedelta(seconds=seconds_ago)

        timestamp = now - delta
        reading = RssiReading(badge_id='a', pi_id='b', timestamp=timestamp)
        return reading

    def test_one_second_ago(self):
        rr = self.reading_with_timestamp(1)
        output = rr.timestamp_ago
        self.assertEqual('1 sec ago', output)

    def test_66_seconds_ago(self):
        rr = self.reading_with_timestamp(66)
        output = rr.timestamp_ago
        self.assertEqual('1 min ago', output)

    def test_66_minutes_ago(self):
        rr = self.reading_with_timestamp(66 * 60)
        output = rr.timestamp_ago
        self.assertEqual('1 hrs ago', output)

    def test_two_days_ago(self):
        rr = self.reading_with_timestamp(86400 * 2.3)
        output = rr.timestamp_ago
        self.assertEqual('2 days ago', output)



class TestRssiReadingValidation(BaseTest):

    def validReading(self):
        from stethoscope.models.rssi_reading import RssiReading
        reading = RssiReading(badge_id='a', badge_strength=-60, pi_id='b', beacon_1_id='c', beacon_1_strength=-20)
        return reading

    def validReadingNoBeacons(self):
        from stethoscope.models.rssi_reading import RssiReading
        reading = RssiReading(badge_id='a', badge_strength=-60, pi_id='b')
        return reading

    def test_happy_path(self):
        rr = self.validReading()
        self.assertTrue(rr.valid)

    def test_happy_path_no_beacons(self):
        rr = self.validReadingNoBeacons()
        self.assertTrue(rr.valid)

    def test_fails_del_no_badge_id(self):
        rr = self.validReading()
        rr.badge_id = None
        self.assertFalse(rr.valid)
        self.assertTrue(rr.invalid)

    def test_fails_del_no_pi_id(self):
        rr = self.validReading()
        rr.pi_id = None
        self.assertFalse(rr.valid)
        self.assertTrue(rr.invalid)

class TestRssiReadingLatestForBadge(BaseTest):

    def setUp(self):
        super(TestRssiReadingLatestForBadge, self).setUp()
        self.init_database()

    def validReading(self):
        from stethoscope.models.rssi_reading import RssiReading
        reading = RssiReading(badge_id='a', badge_strength=-65, pi_id='b', beacon_1_id='c', beacon_1_strength=-20)
        return reading

    def test_returns_latest_reading(self):
        from stethoscope.models.rssi_reading import RssiReading

        reading_1 = self.validReading()
        reading_1.timestamp = datetime.datetime.now() - datetime.timedelta(seconds=20)

        reading_2 = self.validReading()

        reading_3_other_badge = self.validReading()
        reading_3_other_badge.badge_id = 'something_else'

        self.session.add(reading_1)
        self.session.add(reading_2)
        self.session.add(reading_3_other_badge)

        latest_reading = RssiReading.most_recent_from_badge(self.session,
                                                            reading_1.badge_id)


        self.assertEqual(reading_2, latest_reading)



