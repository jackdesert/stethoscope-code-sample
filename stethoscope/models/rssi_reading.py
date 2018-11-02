from datetime import datetime
from sqlalchemy import (
    Column,
    DateTime,
    Index,
    Integer,
    Text,
)

from collections import OrderedDict
from datetime import datetime
from datetime import timedelta
from sqlalchemy import desc
from .meta import Base

import redis
import pdb

class RssiReading(Base):

    __tablename__ = 'rssi_readings'
    id = Column(Integer, primary_key=True)
    badge_id    = Column(Text, nullable=False)
    beacon_1_id = Column(Text)
    beacon_2_id = Column(Text)
    beacon_3_id = Column(Text)
    beacon_4_id = Column(Text)
    beacon_5_id = Column(Text)
    beacon_1_strength = Column(Integer)
    beacon_2_strength = Column(Integer)
    beacon_3_strength = Column(Integer)
    beacon_4_strength = Column(Integer)
    beacon_5_strength = Column(Integer)
    # TODO Do we really need to store pi_id with this model?
    pi_id       = Column(Text, nullable=False)
    timestamp   = Column(DateTime, default=datetime.now)

    # Note badge_id is included, but not pi_id because we will get the
    # same payload from multiple pis, and we only need it from one
    DEDUP_FIELDS = ('badge_id', 'beacon_1_id', 'beacon_2_id', 'beacon_3_id',
                    'beacon_4_id', 'beacon_5_id',
                    'beacon_1_strength', 'beacon_2_strength', 'beacon_3_strength',
                    'beacon_4_strength', 'beacon_5_strength')

    REDIS = redis.StrictRedis(host='localhost', port=6379, db=0)

    # See doc/deduplication_scheme.md
    DEDUP_PERIOD_IN_MILLISECONDS = 5500

    RECENT_SECONDS = 60

    NULL_BEACON_STRENGTH = -128

    @property
    def valid(self):
        errors = []
        if not self.badge_id:
            errors.append('badge_id missing')
        if not self.pi_id:
            errors.append('pi_id missing')
        if self.beacon_1_strength == None:
            errors.append(f'beacon_1_strength cannot be None')
        if self.beacon_1_strength == 0:
            errors.append(f'beacon_1_strength cannot be zero')
        self.errors = errors
        return not errors

    @property
    def invalid(self):
        return not self.valid

    def to_dict(self):
        columns = self.__table__.columns.keys()
        return { k:v for k,v in self.__dict__.items() if k in columns }

    def print(self):
        print(f'id: {self.id}')
        print(f'badge: {self.badge_id}')
        print(f'pi: {self.pi_id}')
        print('beacons:')
        print(f'  {self.beacon_1_id}: {self.beacon_1_strength}')
        print(f'  {self.beacon_2_id}: {self.beacon_2_strength}')
        print(f'  {self.beacon_3_id}: {self.beacon_3_strength}')
        print(f'  {self.beacon_4_id}: {self.beacon_4_strength}')
        print(f'  {self.beacon_5_id}: {self.beacon_5_strength}')
        print(f'timestamp: {self.timestamp}')

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
                                 px=self.DEDUP_PERIOD_IN_MILLISECONDS,
                                 nx=True)
        # If it was written, it's original
        return written

    @property
    def beacons(self):
        output = []
        for i in range(1, 6):
            bid = getattr(self, f'beacon_{i}_id')
            bstrength = getattr(self, f'beacon_{i}_strength')
            if bid and (bstrength > self.NULL_BEACON_STRENGTH):
                output.append((bid, bstrength))

        return output

    @property
    def _redis_dedup_key(self):
        values = (str(self.__dict__.get(key)) for key in self.DEDUP_FIELDS)
        specific = '|'.join(values)
        return f'rssi_reading__{specific}'

    @property
    def timestamp_ago(self):
        delta = datetime.now() - self.timestamp
        sec = delta.total_seconds()
        if sec < 60:
            return f'{ round(sec) } sec ago'
        elif sec < 3600:
            return f'{ round(sec/60) } min ago'
        elif sec < 86400:
            return f'{ round(sec/3600) } hrs ago'
        else:
            return f'{ round(sec/86400) } days ago'

    @classmethod
    def recent_badge_ids(cls, session):
        one_minute_ago = datetime.now() - timedelta(seconds=cls.RECENT_SECONDS)
        badge_ids = [ id for (id,) in session.query(RssiReading.badge_id).distinct().all() ]
        rows = session.query(RssiReading.badge_id). \
                           filter(RssiReading.timestamp > one_minute_ago). \
                           distinct()

        return [ id for (id,) in rows.all()]

    @classmethod
    def most_recent_from_badge(cls, session, badge_id):
        row = session.query(cls).filter_by(badge_id=badge_id).order_by(desc(cls.timestamp)).limit(1)

        return row[0]






Index('rssi_readings__badge_id', RssiReading.badge_id)
