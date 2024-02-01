test:
	python -m pytest -p tests -s

lint-and-format:
	./scripts/format_and_lint.sh

dev_docker_alias := docker-compose --file=./docker-compose.dev.yml
start-docker-dev:
	$(dev_docker_alias) up
stop-docker-dev:
	$(dev_docker_alias) down
remove-volumes-docker-dev:
	$(dev_docker_alias) down && $(dev_docker_alias) rm -v
