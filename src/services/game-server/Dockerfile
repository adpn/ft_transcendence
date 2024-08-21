FROM		python:3.11-slim

RUN			pip install django channels uvicorn[standard]

COPY		src /home/service
COPY		tools/run_service.sh /bin/run_service.sh

RUN			chmod +x /bin/run_service.sh

EXPOSE		8000

ENTRYPOINT	[ "run_service.sh" ]
