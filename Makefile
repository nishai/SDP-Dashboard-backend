
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
	@python manage.py migrate

run: migrate
	@python manage.py runserver

check:
	@python manage.py check --deploy

clean-data:
	@make -C $(DATA_DIR) clean-data

clean: clean-data

# vars
CONTAINER_NAME = dashboard-backend-server
IMAGE_NAME     = dashboard-backend
DIR_VOL        = $(shell pwd)/data
DIR_MNT        = /usr/src/dashboard-backend/data
RUN_PARAMS     = --rm -it -v "$(DIR_VOL):$(DIR_MNT)" --name "$(CONTAINER_NAME)"

docker-build:
	docker build -t "$(IMAGE_NAME)" ./

docker-migrate: docker-build
	docker run $(RUN_PARAMS) $(IMAGE_NAME) migrate

docker-run: docker-migrate
	docker run $(RUN_PARAMS) -p "8000:8000" $(IMAGE_NAME)

docker-check: docker-build
	docker run $(RUN_PARAMS) $(IMAGE_NAME) check --deploy
