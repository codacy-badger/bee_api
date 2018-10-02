import datetime
from sqlalchemy import *
from sqlalchemy.orm import (relationship)
from bee_api.database import Base


class Hive(Base):
    __tablename__ = "hive"
    id = Column(Integer, primary_key=True)
    ownerId = Column(Integer, ForeignKey('user.id'))
    owner = relationship('User', backref='hives')
# Hive location may differ from the location of the bee keeper
    locationId = Column(Integer, ForeignKey('location.id'))
    location = relationship('Location', backref='hives')
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_update = Column(DateTime, default=datetime.datetime.utcnow)
#    door_open = Column(Boolean, server_default=True)


class HiveData(Base):
    __tablename__ = "hiveData"
    id = Column(Integer, primary_key=True)
    hiveId = Column(Integer, ForeignKey('hive.id'))
    hive = relationship('Hive', backref='hiveData')
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    temperature = Column(Numeric)
    humidity = Column(Numeric)
    sensor = Column(Integer)
    outdoor = Column(BOOLEAN)
