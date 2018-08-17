import pdb
import transaction
import unittest

from pyramid import testing


def dummy_request(dbsession):
    return testing.DummyRequest(dbsession=dbsession)


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp(settings={
            'sqlalchemy.url': 'sqlite:///:memory:'
        })
        self.config.include('.models')
        settings = self.config.get_settings()

        from .models import (
            get_engine,
            get_session_factory,
            get_tm_session,
            )

        self.engine = get_engine(settings)
        session_factory = get_session_factory(self.engine)

        self.session = get_tm_session(session_factory, transaction.manager)

    def init_database(self):
        from .models.meta import Base
        Base.metadata.create_all(self.engine)

    def tearDown(self):
        from .models.meta import Base

        testing.tearDown()
        transaction.abort()
        Base.metadata.drop_all(self.engine)


class TestMyViewSuccessCondition(BaseTest):

    def setUp(self):
        super(TestMyViewSuccessCondition, self).setUp()
        self.init_database()

        from .models import MyModel

        model = MyModel(name='one', value=55)
        self.session.add(model)

    def test_passing_view(self):
        from .views.default import my_view
        info = my_view(dummy_request(self.session))
        self.assertEqual(info['one'].name, 'one')
        self.assertEqual(info['project'], 'stethoscope')


class TestMyViewFailureCondition(BaseTest):

    def test_failing_view(self):
        from .views.default import my_view
        info = my_view(dummy_request(self.session))
        self.assertEqual(info.status_int, 500)


############  RssiReadings View Tests Written by Jack  #########################

class TestHaberdasher(BaseTest):

    def setUp(self):
        super(TestHaberdasher, self).setUp()
        self.init_database()

        #from .models import MyModel

        #model = MyModel(name='one', value=55)
        #self.session.add(model)

    def params(self):
        # Instantiating out of order to make sure
        # it is sorting *by value*
        return dict(badge_id='badge_0',
                    pi_id='pi_0',
                    beacons=dict(a=10, b=30, d=20, e=40, c=50, f=0))


    def test_ordered_beacons(self):
        from .views.default import haberdasher
        import json

        req = dummy_request(self.session)
        req.body = json.dumps(self.params())
        info = haberdasher(req)
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
        from .views.default import haberdasher
        import json

        req = dummy_request(self.session)
        params = self.params()
        del params['beacons']['c']
        del params['beacons']['e']
        del params['beacons']['a']
        del params['beacons']['f']
        req.body = json.dumps(params)
        info = haberdasher(req)
        self.assertEqual(info, {'badge_id': 'badge_0',
                                'pi_id': 'pi_0',
                                'beacon_1_id': 'b',
                                'beacon_2_id': 'd',
                                'beacon_1_strength': 30,
                                'beacon_2_strength': 20},
                          'Returns 2 in sorted order')

#class TestMyViewFailureCondition(BaseTest):
#
#    def test_failing_view(self):
#        from .views.default import my_view
#        info = my_view(dummy_request(self.session))
#        self.assertEqual(info.status_int, 500)
#                    beacon_1_id='x',
#                    beacon_2_id='y',
#                    beacon_3_id='z',
#                    beacon_1_strength=10,
#                    beacon_2_strength=20,
#                    beacon_3_strength=30)


############ RssiReading  Model Tests Written by Jack  #########################

class TestRssiReadingDuplicate(BaseTest):

    def setUp(self):
        # Flush Redis before each test
        super(TestRssiReadingDuplicate, self).setUp()
        from .models.rssi_reading import RssiReading
        redis = RssiReading.REDIS
        redis.flushall()

    def reading(self):
        from .models.rssi_reading import RssiReading

        reading = RssiReading(badge_id='a',
                              pi_id='b',
                              beacon_1_id='x',
                              beacon_2_id='y',
                              beacon_3_id='z',
                              beacon_1_strength=10,
                              beacon_2_strength=20,
                              beacon_3_strength=30)

        return reading

    def test_once(self):
        rr = self.reading()
        self.assertFalse(rr.duplicate)

    def test_twice(self):
        rr = self.reading()
        self.assertFalse(rr.duplicate, 'first time expected to be unique')
        self.assertTrue(rr.duplicate, 'second time expected to be duplicate')
        self.assertTrue(rr.duplicate, 'third time expected to be duplicate')
        self.assertTrue(rr.duplicate, 'fourth time expected to be duplicate')

    def test_with_literal_delays(self):
        import time
        first_delay = 4.4
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

        rr.beacon_1_id += '-'
        self.assertFalse(rr.duplicate, 'expected unique del beacon_1_id changed')

        rr.beacon_2_id += '-'
        self.assertFalse(rr.duplicate, 'expected unique del beacon_2_id changed')

        rr.beacon_3_id += '-'
        self.assertFalse(rr.duplicate, 'expected unique del beacon_3_id changed')

        rr.beacon_1_strength += 1
        self.assertFalse(rr.duplicate, 'expected unique del beacon_1_strength changed')

        rr.beacon_2_strength += 1
        self.assertFalse(rr.duplicate, 'expected unique del beacon_2_strength changed')

        rr.beacon_3_strength += 1
        self.assertFalse(rr.duplicate, 'expected unique del beacon_3_strength changed')



class TestRssiReadingTimestampAgo(BaseTest):

    def reading_with_timestamp(self, seconds_ago):
        import datetime
        from .models.rssi_reading import RssiReading
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
        from .models.rssi_reading import RssiReading
        reading = RssiReading(badge_id='a', pi_id='b')
        return reading

    def test_happy_path(self):
        rr = self.validReading()
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


############ TrainingRun Model Tests Written by Jack  #########################

class TestTrainingRun(BaseTest):


    def validTrainingRun(self):
        from .models.training_run import TrainingRun

        training_run = TrainingRun(room_id='a',
                                   badge_id='b')
        return training_run


    def test_happy_path(self):
        run = self.validTrainingRun()
        self.assertTrue(run.valid)

    def test_fails_del_no_badge_id(self):
        run = self.validTrainingRun()
        run.badge_id = None
        self.assertFalse(run.valid)
        self.assertTrue(run.invalid)

    def test_fails_del_no_room_id(self):
        run = self.validTrainingRun()
        run.room_id = None
        self.assertFalse(run.valid)
        self.assertTrue(run.invalid)



############  TrainingRun View Tests Written by Jack  #########################

class TestTrainingRunBulkStart(BaseTest):

    def setUp(self):
        super(TestTrainingRunBulkStart, self).setUp()
        self.init_database()

    def params(self):
        # Instantiating out of order to make sure
        # it is sorting *by value*
        return dict(room_id='room_a',
                    badge_ids=['badge_a', 'badge_b'])


    def test_happy_path(self):
        from .views.training_runs import training_runs__bulk_start_view
        import json

        req = dummy_request(self.session)
        req.body = json.dumps(self.params())

        info = training_runs__bulk_start_view(req)
        self.assertEqual(req.response.status_code, 201)
        self.assertEqual(info, {'training_run_ids': [1,2]})

    def test_fails_no_room_id(self):
        from .views.training_runs import training_runs__bulk_start_view
        import json

        req = dummy_request(self.session)
        params = self.params()
        params['room_id'] = None
        req.body = json.dumps(params)

        info = training_runs__bulk_start_view(req)
        self.assertEqual(req.response.status_code, 400)
        self.assertEqual(info, {'error': 'Please supply room_id'})


class TestTrainingRunBulkEnd(BaseTest):

    def setUp(self):
        super(TestTrainingRunBulkEnd, self).setUp()
        from datetime import datetime
        from .models.training_run import TrainingRun

        self.init_database()
        now = datetime.now()

        run_1 = TrainingRun(start_timestamp=now,
                            room_id='room_a',
                            badge_id='badge_1')

        run_2 = TrainingRun(start_timestamp=now,
                            room_id='room_a',
                            badge_id='badge_1')
        self.session.add(run_1)
        self.session.add(run_2)
        self.session.flush()

        self.training_run_ids = [run_1.id, run_2.id]


    def test_happy_path(self):
        from .models.training_run import TrainingRun
        from .views.training_runs import training_runs__bulk_end_view
        import json

        req = dummy_request(self.session)
        params = dict(training_run_ids=self.training_run_ids)
        req.body = json.dumps(params)

        info = training_runs__bulk_end_view(req)
        self.assertEqual(req.response.status_code, 200)
        for id in self.training_run_ids:
            t_run = self.session.query(TrainingRun).get(id)
            self.assertIsNotNone(t_run.end_timestamp, 'Expected an end_timestamp')

    def test_fails_no_training_run_ids(self):
        from .views.training_runs import training_runs__bulk_end_view
        import json

        req = dummy_request(self.session)
        params = dict(something_else_entirely=self.training_run_ids)
        req.body = json.dumps(params)

        info = training_runs__bulk_end_view(req)
        self.assertEqual(req.response.status_code, 400)
        self.assertEqual(info, {'error': 'Please supply training_run_ids'})

class TestTrainingRunBulkStats(BaseTest):

    def setUp(self):
        super(TestTrainingRunBulkStats, self).setUp()
        from datetime import datetime
        from datetime import timedelta
        from .models.training_run import TrainingRun
        from .models.rssi_reading import RssiReading

        self.init_database()
        now = datetime.now()
        one_minute_ago  = now - timedelta(seconds=60)
        two_minutes_ago = now - timedelta(seconds=120)


        # Completed
        completed_run = TrainingRun(start_timestamp=two_minutes_ago,
                        end_timestamp=now,
                        room_id='room_a',
                        badge_id='badge_1')


        reading_for_completed_1 = RssiReading(badge_id='badge_1',
                                       timestamp=one_minute_ago,
                                       beacon_1_id='abc',
                                       pi_id='x',
                                       beacon_1_strength=50)

        reading_for_completed_2 = RssiReading(badge_id='badge_1',
                                       timestamp=one_minute_ago,
                                       beacon_1_id='abc',
                                       pi_id='x',
                                       beacon_1_strength=51)



        # In-Progress
        run_in_progress_1 = TrainingRun(start_timestamp=one_minute_ago,
                            room_id='room_a',
                            badge_id='badge_1')

        run_in_progress_2 = TrainingRun(start_timestamp=one_minute_ago,
                            room_id='room_a',
                            badge_id='badge_2')


        reading_during_1 = RssiReading(badge_id='badge_1',
                                       timestamp=now,
                                       beacon_1_id='abc',
                                       pi_id='x',
                                       beacon_1_strength=52)

        reading_during_2 = RssiReading(badge_id='badge_1',
                                       timestamp=now,
                                       beacon_1_id='abc',
                                       pi_id='x',
                                       beacon_1_strength=53)

        self.session.add(completed_run)
        self.session.add(run_in_progress_1)
        self.session.add(run_in_progress_2)
        self.session.add(reading_for_completed_1)
        self.session.add(reading_for_completed_2)
        self.session.add(reading_during_1)
        self.session.add(reading_during_2)
        self.session.flush()

        self.training_run_ids = [run_in_progress_1.id, run_in_progress_2.id]

    def params(self):
            return dict(room_id='room_a',
                        training_run_ids=self.training_run_ids)


    def test_happy_path(self):
        from .models.training_run import TrainingRun
        from .views.training_runs import training_runs__bulk_stats_view
        import json

        req = dummy_request(self.session)
        req.body = json.dumps(self.params())

        info = training_runs__bulk_stats_view(req)
        self.assertEqual(req.response.status_code, 200)
        expected = { 'in_progress': { 'badge_1': 2,
                                      'badge_2': 0, },
                     'in_progress_total': 2,
                     'completed': 2,
                     'total': 4 }

        self.assertEqual(info, expected)
