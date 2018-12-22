FROM tiangolo/uwsgi-nginx-flask:python3.7

COPY ./bee_api/app /app/app/
COPY ./bee_api/classes /app/classes/
COPY ./bee_api/fixtures /app/fixtures/
COPY ./bee_api/helpers /app/helpers
COPY ./bee_api/migrations /app/migrations/
COPY ./bee_api/config.py /app/config.py
COPY ./bee_api/database.py /app/database.py
COPY ./bee_api/manage.py /app/manage.py
COPY ./bee_api/routes.py /app/routes.py
COPY ./bee_api/run.py /app/run.py
COPY ./bee_api/schema.py /app/schema.py
#COPY ./bee_api/wsgi.py /app/wsgi.py
COPY ./bee_api/uwsgi.ini /app/uwsgi.ini
COPY ./bee_api/requirements.txt /app/requirements.txt

EXPOSE 8000
RUN pip install -r /app/requirements.txt
