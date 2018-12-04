
from datetime import datetime
from sqlalchemy import (
    Column,
    DateTime,
    Index,
    Integer,
    Text,
    text,
    desc,
)
from sqlalchemy.sql import func
from collections import namedtuple


from .meta import Base
from .rssi_reading import RssiReading
import numpy as np
import ipdb

# namedtuple must be defined outside the class so the unpickler can find it
KerasMetadata = namedtuple('KerasMetadata', ['room_ids', 'beacon_id_to_beacon_index', 'strength_range', 'min_strength'])

class TrainingRunExpectedCompleteError(Exception):
    '''Expectation not met: Either training run is complete
       (has start_timestamp and end_timestamp) but expectation was false,
       or vice versa'''

class TrainingRun(Base):
    __tablename__ = 'training_runs'
    id              = Column(Integer, primary_key=True)
    room_id         = Column(Text)
    badge_id        = Column(Text, nullable=False)
    start_timestamp = Column(DateTime)
    end_timestamp   = Column(DateTime)
    created_by      = Column(Text)


    @property
    def valid(self):
        errors = []
        if not self.badge_id:
            errors.append('badge_id is missing')
        if not self.room_id:
            errors.append('room_id is missing')
        return not errors

    @property
    def invalid(self):
        return not self.valid


    def rssi_readings(self, session, expected_complete):
        # Raise exception if this TrainingRun is not in the
        # state you expect
        if not expected_complete == bool(self.end_timestamp):
            raise TrainingRunExpectedCompleteError

        readings = session.query(RssiReading). \
                   filter(RssiReading.badge_id == self.badge_id). \
                   filter(RssiReading.timestamp > self.start_timestamp)

        if expected_complete:
            readings = readings.filter(RssiReading.timestamp < self.end_timestamp)

        return readings

    def count_rssi_readings(self, session, expected_complete):
        self.count_rssi_readings_memoized = self.rssi_readings(session, expected_complete).count()
        return self.count_rssi_readings_memoized

    def print(self):
        print(f'id: {self.id}')
        print(f'room: {self.room_id}')
        print(f'badge: {self.badge_id}')
        print(f'start_timestamp: {self.start_timestamp}')
        print(f'end_timestamp: {self.end_timestamp}')

    # Stethoscope cannot reliably predict location for rssi events created
    # when there was a different set of training runs and/or a different
    # set of beacons active. Therefore we ask "When was the lasts approved
    # training run?", meaning which is the last training run where Jack
    # has manually updated the "created_by" column.
    # Because manually updating the "created_by" column is what Jack
    # does when he trains the keras model.
    @classmethod
    def last_approved_timestamp(cls, session):
        trun = session.query(cls).\
                    filter(cls.end_timestamp.isnot(None)).\
                    filter(cls.created_by.isnot(None)).\
                    order_by(desc(cls.end_timestamp)).\
                    first()
        if trun:
            return trun.end_timestamp
        else:
            # Test environment may not have training runs
            return datetime.now()


    @classmethod
    def with_ids(cls, session, ids):
        return session.query(cls).filter(cls.id.in_(ids))

    @classmethod
    def completed_for_room(cls, session, room_id):
        return session.query(cls).filter_by(room_id=room_id).\
                                  filter(cls.end_timestamp.isnot(None))

    @classmethod
    def completed(cls, session):
        return session.query(cls).filter(cls.end_timestamp.isnot(None))

    @classmethod
    def distinct_room_ids(cls, session):
        room_ids = [ id for (id, ) in session.query(TrainingRun.room_id).distinct().all() ]
        # Sort room_ids so they always show up in the same order
        room_ids.sort()
        return room_ids

    @classmethod
    def distinct_beacon_ids(cls, session):
        # This returns beacon_ids ONLY from rssi readings that are
        # attached to completed training runs
        beacon_ids = set()
        reading_ids = cls.rssi_reading_ids_from_all_completed_training_runs(session)
        qobjects = [RssiReading.beacon_1_id,
                    RssiReading.beacon_2_id,
                    RssiReading.beacon_3_id,
                    RssiReading.beacon_4_id,
                    RssiReading.beacon_5_id]
        for qq in qobjects:
            rows = session.query(qq).filter(RssiReading.id.in_(reading_ids)).distinct()
            for (id,) in rows:
                if id:
                    beacon_ids.add(id)
        return sorted(list(beacon_ids))




    @classmethod
    def rssi_reading_ids_from_all_completed_training_runs(cls, session):
        sql = '''SELECT rssi_readings.id FROM rssi_readings
                  JOIN training_runs
                    ON rssi_readings.badge_id = training_runs.badge_id
                  WHERE  training_runs.end_timestamp IS NOT NULL
                    AND  rssi_readings.timestamp BETWEEN
                                                        training_runs.start_timestamp
                                                        AND
                                                        training_runs.end_timestamp;
              '''

        rows = session.query(RssiReading.id).from_statement(text(sql))
        return [id for (id,) in rows]


    @classmethod
    def data_and_labels(cls, session):
        room_ids = cls.distinct_room_ids(session)
        room_id_to_room_index = { rid : ridx for (ridx,rid) in enumerate(room_ids) }

        beacon_ids = cls.distinct_beacon_ids(session)
        beacon_id_to_beacon_index = { bid : bidx for (bidx,bid) in enumerate(beacon_ids) }
        distinct_beacon_count = len(beacon_ids)
        reading_ids = cls.rssi_reading_ids_from_all_completed_training_runs(session)
        num_readings = len(reading_ids)
        reading_ids_set = set(reading_ids)

        # Normalize Data, part 1
        max_strength = session.query(func.max(RssiReading.beacon_1_strength)).scalar()
        mins = session.query(func.min(RssiReading.beacon_1_strength),
                             func.min(RssiReading.beacon_2_strength),
                             func.min(RssiReading.beacon_3_strength),
                             func.min(RssiReading.beacon_4_strength),
                             func.min(RssiReading.beacon_5_strength))

        # Use padding near zero so no actual readings are conflated with zero
        min_padding = 10
        min_strength = min(mins[0]) - min_padding

        # Normalize Data, part 2
        strength_range = max_strength - min_strength

        # Use this metadata to normalize real-time data
        # before passing it to keras.models.Sequential.predict()
        metadata = KerasMetadata(room_ids,
                                 beacon_id_to_beacon_index,
                                 strength_range,
                                 min_strength)


        data = np.zeros((num_readings, distinct_beacon_count), dtype='float')
        labels = np.zeros(num_readings, dtype='int8')


        index = 0
        for t_run in cls.completed(session):
            for reading in t_run.rssi_readings(session, True):
                reading_ids_set.remove(reading.id)
                vectorized_reading, _ = NeuralNetworkHelper.vectorize_and_normalize_reading(reading,
                                                                                         metadata)
                data[index] = vectorized_reading

                room_index = room_id_to_room_index[t_run.room_id]
                labels[index] = room_index
                index += 1

        # Verify that each reading_id was added to `data` exactly once
        # by checking that `reading_ids_set` is now empty.
        # This is to make sure that each reading only belongs to a single
        # TrainingRun
        # and is a stronger check than simply verifying that
        #   len(reading_ids) == `the number of times the inner loop runs`
        assert reading_ids_set == set()





        # `data` is vectorized because that is the best way I know of to
        # return the data as a numpy array
        #
        # `labels` is not vectorized, but will need to be vectorized before
        # it is fed into the keras model
        return data, labels, metadata



# Loading this at the end of the file so that circular imports do not break it
# See http://effbot.org/zone/import-confusion.htm

from .neural_network_helper import NeuralNetworkHelper
