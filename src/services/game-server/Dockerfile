FROM		alpine:3.20

RUN			apk update && apk upgrade && apk add \
			python3-dev \
			build-base \
			py3-pip \
			py3-django \
			py3-channels \
			uvicorn

# RUN			pip install uvicorn
COPY		src /home/service
COPY		tools/run_service.sh /bin/run_service.sh

RUN			chmod +x /bin/run_service.sh

EXPOSE		8000

ENTRYPOINT	[ "run_service.sh" ]
