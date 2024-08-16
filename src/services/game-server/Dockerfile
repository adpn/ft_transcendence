FROM		python:3.11

RUN	pip install django channels uvicorn[standard]

# RUN			pip install uvicorn
COPY		src /home/service
COPY		tools/run_service.sh /bin/run_service.sh

RUN			chmod +x /bin/run_service.sh

EXPOSE		8000

ENTRYPOINT	[ "run_service.sh" ]
