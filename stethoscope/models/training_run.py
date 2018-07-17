
from datetime import datetime
from sqlalchemy import (
    Column,
    DateTime,
    Index,
    Integer,
    Text,
)

from .meta import Base

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

    def print(self):
        print(f'id: {self.id}')
        print(f'room: {self.room_id}')
        print(f'badge: {self.badge_id}')
        print(f'start_timestamp: {self.start_timestamp}')
        print(f'end_timestamp: {self.end_timestamp}')
