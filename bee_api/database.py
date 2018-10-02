
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (create_engine, MetaData)
from sqlalchemy.orm import (sessionmaker, scoped_session)
from flask_migrate import Migrate
from bee_api.app import app

Base = declarative_base()

engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'],
                       convert_unicode=True)
metadata = MetaData(engine)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base.query = db_session.query_property()

db = SQLAlchemy(app)
db.session = db_session
migrate = Migrate(app, db)


def init_db():
    metadata.create_all(bind=engine)
    for _t in metadata.tables:
        print("Table: ", _t)
