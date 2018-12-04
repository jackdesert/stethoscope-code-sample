from ..models.neural_network_helper import NoMatchingBeaconsError
from ..models.rssi_reading import RssiReading
from ..models.training_run import TrainingRun
from ..models.util import PrudentIterator
from collections import defaultdict
from datetime import datetime
from datetime import timedelta
import ipdb
import pdb
import operator



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

    # Pass in keras_model and keras_metadata when running tests
    def __init__(self, session,
                       location_predictor,
                       badge_id,
                       algorithm=DEFAULT_ALGORITHM,
                       date_string=None,
                       grain=DEFAULT_GRAIN,
                       return_value=DEFAULT_RETURN_VALUE):
        self.session = session
        self.predictor = location_predictor
        self.badge_id = badge_id
        self._set_timestamps(date_string)
        self.grain = grain
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
        metadata = dict(   algorithm = self.algorithm,
                               grain = self.grain,
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
        scorekeeper = defaultdict(int)

        num_periods = self.SECONDS_PER_DAY // self.grain

        periods = [self.start_timestamp + delta * index for index in range(num_periods)]

        di = PrudentIterator(self.data)

        for period in periods:
            while di.available and (di.peek[0] < period + delta):
                (timestamp, room) = di.next
                scorekeeper[room] += 1

            if scorekeeper:
                winning_room = max(scorekeeper.items(), key=operator.itemgetter(1))[0]
                summary.append((period, winning_room))
            else:
                summary.append((period, None))

            scorekeeper.clear()


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
            except NoMatchingBeaconsError as ee:
                error = 'NO MATCHING BEACONS'

            if reading.timestamp < self.last_approved_timestamp:
                value = 'READING PREDATES TR'
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

    def _set_timestamps(self, date_string):
        if not date_string:
            date_string = datetime.now().strftime(self.DATE_FORMAT)

        self.start_timestamp = datetime.strptime(date_string, self.DATE_FORMAT)
        self.end_timestamp   = self.start_timestamp + timedelta(days=1)


