test:
	python -m pytest -p tests -s

lint-and-format:
	./scripts/format_and_lint.sh

dev_docker_alias := docker-compose --file=./docker-compose.dev.yml
start-dev-docker:
	$(dev_docker_alias) up
stop-dev-docker:
	$(dev_docker_alias) down
