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
from bee_api import models          # This line
config.set_main_option('sqlalchemy.url',
                       current_app.config.get('SQLALCHEMY_DATABASE_URI'))
target_metadata = models.Base.metadata # And this line
```
