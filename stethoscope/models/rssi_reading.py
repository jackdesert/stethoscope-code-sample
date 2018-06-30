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


class RssiReading(Base):
    __tablename__ = 'rssi_readings'
    id = Column(Integer, primary_key=True)
    badge_id    = Column(Text, nullable=False)
    badge_nonce = Column(Text)
    beacon_1_id = Column(Text)
    beacon_2_id = Column(Text)
    beacon_3_id = Column(Text)
    beacon_1_strength = Column(Float)
    beacon_2_strength = Column(Float)
    beacon_3_strength = Column(Float)
    pi_id       = Column(Text, nullable=False)
    pi_nonce    = Column(Text)
    timestamp   = Column(DateTime, default=datetime.now)

    @property
    def valid(self):
        return True

    def to_dict(self):
        columns = self.__table__.columns.keys()
        return { k:v for k,v in self.__dict__.items() if k in columns }

Index('rssi_readings__badge_id', RssiReading.badge_id)
