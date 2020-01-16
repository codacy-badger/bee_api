# bee_api
![](https://github.com/BeeRaspberry/bee_api/workflows/build/badge.svg)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/7dcc779f81d0483d93f0e7c1c5a735e6)](https://www.codacy.com/gh/BeeRaspberry/bee_api?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=BeeRaspberry/bee_api&amp;utm_campaign=Badge_Grade)

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
```bash
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



