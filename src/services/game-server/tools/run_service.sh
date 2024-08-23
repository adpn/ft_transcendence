#!/bin/sh

# MAX_RETRIES=60

# retries=0

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

cd /home/service && uvicorn src.asgi:application --host 0.0.0.0 --port 8000 --reload
