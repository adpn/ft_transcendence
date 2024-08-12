FROM postgres:16.4-alpine3.20

COPY conf/create_databases.sh /docker-entrypoint-initdb.d/

RUN chmod +x /docker-entrypoint-initdb.d/create_databases.sh