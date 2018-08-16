
DATA_DIR = "./data"

all:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  run                to run the project"
	@echo "  migrate            to migrate the project database"
	@echo "  docker-run   		to run the project (recommended)"
	@echo "  docker-migrate     to migrate the project database (recommended)"
	@echo "  docker-build       to build the docker image"
	@echo "  clean              to clean the entire project"
	@echo "  clean-data         to clean only generated data"

migrate:
	python manage.py migrate

run: migrate
	python manage.py runserver


clean: clean-data

clean-data:
	make -C $(DATA_DIR) clean


docker-build:
	@echo
	@echo "Building Docker Container: dashboard-api"
	@echo "========================================"
	docker build -t dashboard-api ./

docker-migrate: docker-build
	@echo
	@echo "Migrating Docker Container:  dashboard-api"
	@echo "========================================"
	docker run --rm -it -v "$(shell pwd)/data:/usr/src/dashboard-backend/data" --name "dashboard-api-server" dashboard-api migrate

docker-run: docker-migrate
	@echo
	@echo "Running Docker Container:  dashboard-api"
	@echo "========================================"
	docker run --rm -it -v "$(shell pwd)/data:/usr/src/dashboard-backend/data" -p 8000:8000 --name "dashboard-api-server" dashboard-api
