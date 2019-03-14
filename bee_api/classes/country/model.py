from sqlalchemy import *
from database import (Base)

__all__ = ['Country']


class Country(Base):
    __tablename__ = 'country'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200))
    shortName = Column(String(10))
