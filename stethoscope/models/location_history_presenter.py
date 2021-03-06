from ..models.neural_network_helper import DisjointBeaconsError
from ..models.neural_network_helper import NoBeaconsError
from ..models.rssi_reading import RssiReading
from ..models.training_run import TrainingRun
from ..models.util import PrudentIterator
from ..models.util import BiasedScorekeeper
from collections import defaultdict
from datetime import datetime
from datetime import timedelta
import ipdb
import pdb


class LocationHistoryFutureOffsetError(Exception):
    '''If you specify an offset and a date_string,
    and the date_string is in the future,
    this error is raised'''

class LocationHistoryPresenter:

    DATE_FORMAT = '%Y-%m-%d'
    TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S'

    SUPPORTED_ALGORITHMS = ('raw', 'bayes')
    SUPPORTED_RETURN_VALUES = ('room_id', 'room_name')

    DEFAULT_ALGORITHM = 'raw'
    DEFAULT_GRAIN = None
    DEFAULT_RETURN_VALUE = 'room_name'

    SECONDS_PER_DAY = 86400
    PERIOD_END_TEXT = 'Period End'

    NO_BEACONS          = 'NO BEACONS'
    DISJOINT_BEACONS    = 'DISJOINT BEACONS'
    READING_PREDATES_TR = 'READING PREDATES TR'

    TRUMPED_KEYS = {NO_BEACONS, DISJOINT_BEACONS, READING_PREDATES_TR}

    # Pass in keras_model and keras_metadata when running tests
    def __init__(self, session,
                       location_predictor,
                       badge_id,
                       algorithm=DEFAULT_ALGORITHM,
                       date_string=None,
                       offset=None,
                       grain=DEFAULT_GRAIN,
                       return_value=DEFAULT_RETURN_VALUE):
        self.session = session
        self.predictor = location_predictor
        self.badge_id = badge_id
        self._set_timestamps(date_string, offset, grain)
        self.grain = grain
        self.offset = offset
        self.return_value = return_value
        self.algorithm = algorithm
        self.last_approved_timestamp = TrainingRun.last_approved_timestamp(session)
        assert algorithm    in self.SUPPORTED_ALGORITHMS
        assert return_value in self.SUPPORTED_RETURN_VALUES
        assert (grain == None) or isinstance(grain, int)


    def present(self):
        self._fetch_rssi_readings()
        self._generate_data()
        self._summarize()

        # offset is only used if grain also present
        offset_to_display = self.offset
        if offset_to_display and not self.grain:
            offset_to_display = 'ignored because no grain supplied'

        metadata = dict(   algorithm = self.algorithm,
                               grain = self.grain,
                              offset = offset_to_display,
                        return_value = self.return_value,
                        last_approved_training_run = str(self.last_approved_timestamp))

        metadata['num_priors'] = len(self.predictor.priors or [])

        return dict(data=self._formatted_summary(), metadata=metadata)

    def _formatted_summary(self):
        # Format so it can be turned into JSON
        return [(ts.strftime(self.TIMESTAMP_FORMAT), room) for ts, room in self.summary]


    def _summarize(self):
        if not self.grain:
            self.summary = self.data
            return

        summary = []
        last_timestamp = self.start_timestamp
        delta = timedelta(seconds=self.grain)
        next_timestamp = last_timestamp + delta

        span = self.end_timestamp - self.start_timestamp
        span_seconds = span.days * self.SECONDS_PER_DAY + span.seconds
        num_periods = span_seconds // self.grain

        periods = [self.start_timestamp + delta * index for index in range(num_periods)]

        di = PrudentIterator(self.data)

        for period in periods:
            scorekeeper = BiasedScorekeeper(self.TRUMPED_KEYS)

            while di.available and (di.peek[0] < period + delta):
                (timestamp, room) = di.next
                scorekeeper.increment(room)

            winning_room = scorekeeper.winner()
            summary.append((period, winning_room))



        period_end = (self.end_timestamp, self.PERIOD_END_TEXT)
        summary.append(period_end)

        self.summary = summary



    def _generate_data(self):
        predictor = self.predictor
        data = []

        first_index = 0 # Because most probable room is listed first
        second_index = 0 # room_id
        if self.return_value == 'room_name':
            second_index = 2 # room_name


        for reading in self._rssi_readings:
            predictor.reading = reading
            timetamp = reading.timestamp

            error = None
            try:
                location = predictor.location
            except NoBeaconsError:
                error = self.NO_BEACONS
            except DisjointBeaconsError:
                error = self.DISJOINT_BEACONS

            if reading.timestamp < self.last_approved_timestamp:
                value = self.READING_PREDATES_TR
            elif error:
                value = error
            elif location.get('errors'):
                value = None
            else:
                value = location[self.algorithm][first_index][second_index]
            row = (timetamp, value)
            data.append(row)

        # Add one last value so that timeline chart will go up to it
        period_end = (self.end_timestamp, self.PERIOD_END_TEXT)
        data.append(period_end)

        self.data = data

    def _fetch_rssi_readings(self):
        rr = self.session.query(RssiReading) \
                .filter_by(badge_id=self.badge_id) \
                .filter(RssiReading.timestamp.between(self.start_timestamp,
                                                      self.end_timestamp)) \
                .order_by(RssiReading.timestamp)
        self._rssi_readings = rr

    def _set_timestamps(self, date_string, offset, grain):
        if not date_string:
            date_string = datetime.now().strftime(self.DATE_FORMAT)

        # Default timestamps are for a full day
        self.start_timestamp = datetime.strptime(date_string, self.DATE_FORMAT)
        self.end_timestamp   = self.start_timestamp + timedelta(days=1)

        if grain and (offset is not None):

            # Set timestamps to only return specific periods from the day
            # Note you MAY enter this block when offset is zero
            seconds_since_midnight = (datetime.now() - self.start_timestamp).seconds
            completed_periods_since_midnight = seconds_since_midnight // grain
            completed_seconds_since_midnight = completed_periods_since_midnight * grain
            end_delta = timedelta(seconds=completed_seconds_since_midnight)

            if self.start_timestamp.date() == datetime.now().date():
                # If fetching for the current day
                self.end_timestamp = self.start_timestamp + end_delta
            else:
                # If fetching for any other day,
                # end_timestamp remains at the end of the day (start of the next day)
                pass


            start_offset_seconds = grain * offset
            if start_offset_seconds >= self.SECONDS_PER_DAY:
                raise LocationHistoryFutureOffsetError('Offset is greater than 24 hours')
            start_delta = timedelta(seconds=start_offset_seconds)


            self.start_timestamp += start_delta

            now = datetime.now()
            if self.end_timestamp > now:
                msg = 'Offset is present and period ends in the future. Check date_string.'
                raise LocationHistoryFutureOffsetError(msg)
            if self.start_timestamp > now:
                msg = 'Offset is present and period starts in the future. Check offset * grain against current time, or simply try a smaller offset.'
                raise LocationHistoryFutureOffsetError(msg)
            if self.start_timestamp >= self.end_timestamp:
                msg = f'Offset is present but start {self.end_timestamp} is either equal to or later than end {self.start_timestamp}. Check offset * grain against current time, or simply try a smaller offset.'
                raise LocationHistoryFutureOffsetError(msg)


