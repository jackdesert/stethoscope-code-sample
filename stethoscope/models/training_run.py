
from datetime import datetime
from sqlalchemy import (
    Column,
    DateTime,
    Index,
    Integer,
    Text,
    text,
)
from sqlalchemy.sql import func


from .meta import Base
from .rssi_reading import RssiReading
import numpy as np
import pdb


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
        assert expected_complete == bool(self.end_timestamp)

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
    def numpy_tensor(cls, session):
        room_ids = cls.distinct_room_ids(session)
        beacon_ids = cls.distinct_beacon_ids(session)
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



        data = np.zeros((num_readings, distinct_beacon_count), dtype='float')


        index = 0
        for t_run in cls.completed(session):
            for reading in t_run.rssi_readings(session, True):
                reading_ids_set.remove(reading.id)
                for number in range(1, 6):
                    beacon_id = getattr(reading, f'beacon_{number}_id')
                    beacon_strength = getattr(reading, f'beacon_{number}_strength')
                    if beacon_id:
                        data[index][beacon_index] = beacon_strength - min_strength
                index += 1

        # Verify that each reading_id was added to `data` exactly once
        # by checking that `reading_ids_set` is now empty.
        # This is to make sure that each reading only belongs to a single
        # TrainingRun
        # and is a stronger check than simply verifying that
        #   len(reading_ids) == `the number of times the inner loop runs`
        assert reading_ids_set == set()



        # Normalize Data, part 2
        strength_range = max_strength - min_strength
        data /= strength_range


        return data










