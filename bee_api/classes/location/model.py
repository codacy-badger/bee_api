from sqlalchemy import *
from sqlalchemy.orm import (relationship)
from bee_api.database import Base


class Location(Base):
    __tablename__ = 'location'
    id = Column(Integer, primary_key=True, autoincrement=True)
    street_address = Column(String(200))
    city = Column(String(200))
    postal_code = Column(String(20))
    stateProvinceId = Column(Integer, ForeignKey('stateProvince.id'))
    state_province = relationship('StateProvince', backref='location')
