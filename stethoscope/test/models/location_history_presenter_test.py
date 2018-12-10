import pdb
from freezegun import freeze_time
from datetime import datetime
from datetime import timedelta
import pytest
from stethoscope.test.base_test import BaseTest
from stethoscope.models.location_history_presenter import LocationHistoryPresenter
from stethoscope.models.location_history_presenter import LocationHistoryFutureOffsetError

class TestLocationHistoryPresenter(BaseTest):

    # call setUp() so that database will be initialized
    def setUp(self):
        super(TestLocationHistoryPresenter, self).setUp()
        self.init_database()

    def build_presenter(self, args):
        return LocationHistoryPresenter(self.session,
                                        'fake-predictor',
                                        'BIP1234',
                                        **args)


    @property
    def time_format(self):
        return '%Y-%m-%d %H:%M:%S'


    def test_set_timestamps_exception_raised(self):
        exception_data = [
            # GRAIN  OFFSET  DATE_STRING, TIME_FREEZE
            # Offset * grain is more than SECONDS_PER_DAY
            (3600,  24,     None, '2010-10-10 12:15:36'),
            (3600,  25,     None, '2010-10-10 12:15:36'),

            # Offset * grain puts start_timestamp in future
            (3600,   1,     None, '2010-10-10 00:59:00'),

            # Grain and offset present; date_string puts end_timestamp in the future
            (3600, 0,  '2011-01-01', '2010-10-10 12:15:36'),
            (3600, 23, '2011-01-01', '2010-10-10 12:15:36'),

        ]
        for index, (grain, offset, date_string, frozen) in enumerate(exception_data):
            with freeze_time(frozen):
                with pytest.raises(LocationHistoryFutureOffsetError):
                    self.build_presenter(dict(grain=grain,
                                              offset=offset,
                                              date_string=date_string))
                    print(f'index: {index}. Expected exception, but no')

    def test_set_timestamps_happy_path(self):
        # All scenarios where an exception will not be raised...put them in here

        frozen = freeze_time('2010-10-10 12:15:36')
        data = [
            # GRAIN  OFFSET  DATE_STRING    EXPECTED_START         EXPECTED_END
             (None,  None,   None,          '2010-10-10 00:00:00', '2010-10-11 00:00:00'),

            # Setting date string to a date in the future raises an error.
            # See other test

            # Setting date string to a date in the past
             (None,  None,   '2010-09-01',  '2010-09-01 00:00:00', '2010-09-02 00:00:00'),


            # GRAIN  OFFSET  DATE_STRING    EXPECTED_START         EXPECTED_END
            # Grain without offset returns full day
             (3600,  None,   None,          '2010-10-10 00:00:00', '2010-10-11 00:00:00'),
            # Offset without grain returns full day
             (None,  2,      None,          '2010-10-10 00:00:00', '2010-10-11 00:00:00'),


            # GRAIN  OFFSET  DATE_STRING    EXPECTED_START         EXPECTED_END
            # Grain and offset returns only completed periods
             (3600,  0,      None,          '2010-10-10 00:00:00', '2010-10-10 12:00:00'),
             (3600,  1,      None,          '2010-10-10 01:00:00', '2010-10-10 12:00:00'),
             (3600,  11,     None,          '2010-10-10 11:00:00', '2010-10-10 12:00:00'),

            # GRAIN  OFFSET  DATE_STRING    EXPECTED_START         EXPECTED_END
            # Grain and offset and date_string returns up to a full day if in the past
             (3600,  0,      '2010-09-01',  '2010-09-01 00:00:00', '2010-09-02 00:00:00'),
             (3600,  22,     '2010-09-01',  '2010-09-01 22:00:00', '2010-09-02 00:00:00'),
        ]

        for index, (grain, offset, date_string, expected_start, expected_end) in enumerate(data):
            with frozen:
                pr = self.build_presenter(dict(grain=grain,
                                               offset=offset,
                                               date_string=date_string))

                expected_start_object = datetime.strptime(expected_start, self.time_format)
                expected_end_object   = datetime.strptime(expected_end  , self.time_format)


                self.assertEqual(pr.start_timestamp, expected_start_object, f'start: index {index}')
                self.assertEqual(pr.end_timestamp, expected_end_object, f'end: index {index}')







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

