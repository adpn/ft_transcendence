all: build up

build:
	docker compose -f src/docker-compose.yml build

up:
	docker compose -f src/docker-compose.yml up

down:
	docker compose -f src/docker-compose.yml down

clean: down
	docker system prune -af

.PHONY: all build up down clean