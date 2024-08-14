FROM		alpine:3.19

RUN			apk update && apk upgrade && apk add --no-cache \
			python3-dev \
			build-base \
			py3-pip \
			jpeg-dev \
			zlib-dev \
			py3-django \
			py3-psycopg-c

COPY		src /home/service
COPY		tools/run_service.sh /bin/run_service.sh

RUN			chmod +x /bin/run_service.sh

EXPOSE		8000

ENTRYPOINT	[ "run_service.sh" ]
