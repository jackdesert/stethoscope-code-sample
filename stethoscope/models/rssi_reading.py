from datetime import datetime
from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Index,
    Integer,
    Text,
)

from .meta import Base

import redis

class RssiReading(Base):
    __tablename__ = 'rssi_readings'
    id = Column(Integer, primary_key=True)
    badge_id    = Column(Text, nullable=False)
    beacon_1_id = Column(Text)
    beacon_2_id = Column(Text)
    beacon_3_id = Column(Text)
    beacon_1_strength = Column(Float)
    beacon_2_strength = Column(Float)
    beacon_3_strength = Column(Float)
    # TODO Do we really need to store pi_id with this model?
    pi_id       = Column(Text, nullable=False)
    timestamp   = Column(DateTime, default=datetime.now)

    # Note badge_id is included, but not pi_id because we will get the
    # same payload from multiple pis, and we only need it from one
    DEDUP_FIELDS = ('badge_id', 'beacon_1_id', 'beacon_2_id', 'beacon_3_id',
                    'beacon_1_strength', 'beacon_2_strength', 'beacon_3_strength')

    REDIS = redis.StrictRedis(host='localhost', port=6379, db=0)
    DEDUP_PERIOD_IN_SECONDS = 5

    @property
    def valid(self):
        errors = []
        if not self.badge_id:
            errors.append('badge_id missing')
        if not self.pi_id:
            errors.append('pi_id missing')
        self.errors = errors
        return not errors

    @property
    def invalid(self):
        return not self.valid

    def to_dict(self):
        columns = self.__table__.columns.keys()
        return { k:v for k,v in self.__dict__.items() if k in columns }

    @property
    def duplicate(self):
        return not self.original

    @property
    def original(self):
        # "Original", meaning "Not a duplicate"

        # Write key to redis (if does not already exist)
        # and specify an expiration
        written = self.REDIS.set(self._redis_dedup_key,
                                 'Hi Mom', # This field could be anything
                                 ex=self.DEDUP_PERIOD_IN_SECONDS,
                                 nx=True)
        # If it was written, it's original
        return written

    @property
    def _redis_dedup_key(self):
        values = (str(self.__dict__.get(key)) for key in self.DEDUP_FIELDS)
        specific = '|'.join(values)
        return f'rssi_reading__{specific}'


Index('rssi_readings__badge_id', RssiReading.badge_id)
