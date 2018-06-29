from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
)

from .meta import Base


class RssiReading(Base):
    __tablename__ = 'rssi_readings'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    value = Column(Integer)


Index('my_index', RssiReading.name, unique=True, mysql_length=255)
