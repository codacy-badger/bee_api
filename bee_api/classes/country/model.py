from sqlalchemy import *
from bee_api.database import (Base)


class Country(Base):
    __tablename__ = 'country'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200))
    shortNAme = Column(String(10))
