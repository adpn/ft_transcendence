all: build up

detached:
	build upd

build:
	# bash src/setup.sh
	docker compose -f src/docker-compose.yaml build

up:
	docker compose -f src/docker-compose.yaml up

upd:
	docker compose -f src/docker-compose.yaml up -d

down:
	docker compose -f src/docker-compose.yaml down

clean:
	docker compose -f src/docker-compose.yaml down
	docker compose -f src/docker-compose.yaml rm -f
	# bash src/cleanup.sh

fclean: clean
	docker system prune -af

.PHONY: all build up down clean fclean