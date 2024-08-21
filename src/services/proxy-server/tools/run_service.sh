#!/bin/sh

MAX_RETRIES=60

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

retries=0

echo "Waiting for website service to be ready..."
while ! nc -z website 8000; do
	retries=$((retries + 1))
	sleep 1
	if [ $retries -ge $MAX_RETRIES ]; then
		echo "Reached maximum number of retries, exiting..."
		exit 1
	fi
done

echo "Launching proxy-server..."
nginx -g "daemon off;"