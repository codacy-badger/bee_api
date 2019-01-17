# bee_api
[![Build Status](https://travis-ci.org/BeeRaspberry/bee_api.svg?branch=master)](https://travis-ci.org/BeeRaspberry/bee_api)
[![Coverage Status](https://coveralls.io/repos/github/BeeRaspberry/bee_api/badge.svg?branch=master)](https://coveralls.io/github/BeeRaspberry/bee_api?branch=master)
[![codecov](https://codecov.io/gh/BeeRaspberry/bee_api/branch/master/graph/badge.svg)](https://codecov.io/gh/BeeRaspberry/bee_api)

This repo provides the API backend for the web front-end. 

## Work in Progress

## Setup
Notes for myself, as I forget everything.

In order to get `flask db migrate` to work, add the following to `env.py` residing in the `migrations` folder.

```python
from sqlalchemy import engine_from_config, pool
from logging.config import fileConfig
import logging
import classes as models  # this line

config.set_main_option('sqlalchemy.url',
                       current_app.config.get('SQLALCHEMY_DATABASE_URI'))
target_metadata = models.Base.metadata # And this line
```

### Database Commands
#### Migrations
The usual statements
```
python manage.py db init
python manage.py db migrate
python manage.py db upgrade
```
#### Seeding
The process leverages JSON files located in the `fixtures` directory. The file name corresponds with the table it updates. For instance `country.json` updates the `country` table.


After updating the files run
```bash
python manage.py seed
``` 



