all: build up

detached:
	build upd

build:
	bash srcs/setup.sh
	docker compose -f srcs/docker-compose.yaml build

up:
	docker compose -f srcs/docker-compose.yaml up

upd:
	docker compose -f srcs/docker-compose.yaml up -d

down:
	docker compose -f srcs/docker-compose.yaml down

clean:
	docker compose -f srcs/docker-compose.yaml down
	docker compose -f srcs/docker-compose.yaml rm -f
	bash srcs/cleanup.sh

fclean: clean
	docker system prune -af

.PHONY: all build up down clean fclean
