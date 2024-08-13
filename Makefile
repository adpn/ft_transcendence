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

fclean: clean
	docker system prune -af

.PHONY: all detached build up upd down clean fclean
