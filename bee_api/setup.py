from ast import literal_eval
from bee_api import Country
from bee_api import base
import logging
import sys

# Load logging configuration
log = logging.getLogger(__name__)
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


if __name__ == '__main__':
    log.info('Create database {}'.format(base.db_name))
    base.Base.metadata.create_all(base.engine)

    log.info('Insert Country data in database')
    with open('bee_api/fixtures/country.json', 'r') as file:
        data = literal_eval(file.read())
        for record in data:
            country = Country(**record)
            base.db_session.add(country)
        base.db_session.commit()