from pyramid import testing

import datetime
import ipdb
import transaction
import unittest

from stethoscope.test.base_test import BaseTest

def dummy_request(dbsession):
    return testing.DummyRequest(dbsession=dbsession)






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
        from stethoscope.views.training_runs import training_runs__bulk_start_view
        import json

        req = dummy_request(self.session)
        req.body = json.dumps(self.params())

        info = training_runs__bulk_start_view(req)
        self.assertEqual(req.response.status_code, 201)
        self.assertEqual(info, {'training_run_ids': [1,2]})

    def test_fails_no_room_id(self):
        from stethoscope.views.training_runs import training_runs__bulk_start_view
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
        from stethoscope.models.training_run import TrainingRun

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
        from stethoscope.models.training_run import TrainingRun
        from stethoscope.views.training_runs import training_runs__bulk_end_view
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
        from stethoscope.views.training_runs import training_runs__bulk_end_view
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
        from stethoscope.models.training_run import TrainingRun
        from stethoscope.models.rssi_reading import RssiReading

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
        from stethoscope.models.training_run import TrainingRun
        from stethoscope.views.training_runs import training_runs__bulk_stats_view
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
