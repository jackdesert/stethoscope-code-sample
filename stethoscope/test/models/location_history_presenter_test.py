import pdb
from datetime import datetime
from datetime import timedelta
import pytest
from stethoscope.test.base_test import BaseTest
from stethoscope.models.location_history_presenter import LocationHistoryPresenter

class TestLocationHistoryPresenter(BaseTest):

    def build_presenter(self, args):
        return LocationHistoryPresenter('fake-session',
                                        'fake-predictor',
                                        'BIP1234',
                                        **args)


    @property
    def time_format(self):
        return '%Y-%m-%d %H:%M:%S'

    def test__summarize(self):
        presenter = self.build_presenter(dict(grain=3600))
        fake = [
                # first hour
                (2,    'a'),
                (3,    'a'),
                (4,    'a'),

                # second h),ur
                (3602, 'a'),
                (3603, 'a'),
                (3604, 'b'),

                # third hour
                (7202, 'b'),
                (7203, 'c'),
                (7204, 'c')
               ]

        start_timestamp = datetime.strptime('2010-10-10 00:00:00', self.time_format)
        start_delta = timedelta(days=1)
        end_timestamp = start_timestamp + start_delta

        presenter.start_timestamp = start_timestamp
        presenter.end_timestamp = end_timestamp

        delta = timedelta(seconds=1)

        fake_data = []
        for minutes, room in fake:
            timestamp = start_timestamp + minutes * delta
            fake_data.append((timestamp, room))

        presenter.data = fake_data
        presenter._summarize()

        expected = [(datetime(2010, 10, 10, 0, 0), 'a'),
                    (datetime(2010, 10, 10, 1, 0), 'a'),
                    (datetime(2010, 10, 10, 2, 0), 'c'),
                    (datetime(2010, 10, 10, 3, 0), None),
                    (datetime(2010, 10, 10, 4, 0), None),
                    (datetime(2010, 10, 10, 5, 0), None),
                    (datetime(2010, 10, 10, 6, 0), None),
                    (datetime(2010, 10, 10, 7, 0), None),
                    (datetime(2010, 10, 10, 8, 0), None),
                    (datetime(2010, 10, 10, 9, 0), None),
                    (datetime(2010, 10, 10, 10, 0), None),
                    (datetime(2010, 10, 10, 11, 0), None),
                    (datetime(2010, 10, 10, 12, 0), None),
                    (datetime(2010, 10, 10, 13, 0), None),
                    (datetime(2010, 10, 10, 14, 0), None),
                    (datetime(2010, 10, 10, 15, 0), None),
                    (datetime(2010, 10, 10, 16, 0), None),
                    (datetime(2010, 10, 10, 17, 0), None),
                    (datetime(2010, 10, 10, 18, 0), None),
                    (datetime(2010, 10, 10, 19, 0), None),
                    (datetime(2010, 10, 10, 20, 0), None),
                    (datetime(2010, 10, 10, 21, 0), None),
                    (datetime(2010, 10, 10, 22, 0), None),
                    (datetime(2010, 10, 10, 23, 0), None),
                    (datetime(2010, 10, 11, 0, 0), 'Period End')]


        self.assertEqual(expected, presenter.summary)

