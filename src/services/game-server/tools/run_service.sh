#!/bin/sh

MAX_RETRIES=60

retries=0

echo "Waiting for database to be ready..."
while ! nc -z postgresql 5432; do
	retries=$((retries + 1))
	sleep 1
	if [ $retries -ge $MAX_RETRIES ]; then
		echo "Reached maximum number of retries, exiting..."
		exit 1
	fi
done

sleep 5

python3 /home/service/manage.py makemigrations
python3 /home/service/manage.py migrate

cd /home/service && uvicorn src.asgi:application --host 0.0.0.0 --port 8000 --reload
