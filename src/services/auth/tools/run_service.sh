#!/bin/sh

set -e

python3 /home/service/manage.py makemigrations
python3 /home/service/manage.py migrate
# todo: this is temporary need to use uvicorn or gunicorn in the backend.
python3 /home/service/manage.py runserver