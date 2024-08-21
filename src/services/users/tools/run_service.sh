#!/bin/sh

MAX_RETRIES=60

retries=0

echo "Waiting for postgreSQL service to be ready..."
while ! nc -z postgresql 5432; do
	retries=$((retries + 1))
	sleep 1
	if [ $retries -ge $MAX_RETRIES ]; then
		echo "Reached maximum number of retries, exiting..."
		exit 1
	fi
done

retries=0

# echo "Waiting for authentication service to be ready..."
# while ! nc -z user-management 8000; do
# 	retries=$((retries + 1))
# 	sleep 1
# 	if [ $retries -ge $MAX_RETRIES ]; then
# 		echo "Reached maximum number of retries, exiting..."
# 		exit 1
# 	fi
# done

python3 /home/service/manage.py makemigrations
python3 /home/service/manage.py migrate
# todo: this is temporary need to use uvicorn or gunicorn in the backend.
python3 /home/service/manage.py runserver 0.0.0.0:8000
