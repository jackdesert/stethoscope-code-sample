
from datetime import datetime
from sqlalchemy import (
    Column,
    DateTime,
    Index,
    Integer,
    Text,
)

from .meta import Base
from .rssi_reading import RssiReading
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

    def count_rssi_readings(self, session, expected_complete):
        # Raise exception if this TrainingRun is not in the
        # state you expect
        assert expected_complete == bool(self.end_timestamp)

        readings = session.query(RssiReading). \
                   filter(RssiReading.badge_id == self.badge_id). \
                   filter(RssiReading.timestamp > self.start_timestamp)

        if expected_complete:
            readings = readings.filter(RssiReading.timestamp < self.end_timestamp)

        self.count_rssi_readings_memoized = readings.count()
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
