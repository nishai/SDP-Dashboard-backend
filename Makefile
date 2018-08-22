
.DEFAULT_GOAL := help

# =========================================================================	#
# UTIL                                                                      #
# =========================================================================	#

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  migrate            initialise & migrate the database"
	@echo "  run                serve the project in *production mode*"
	@echo "  dev                serve the project in *develop mode*, supports live updates"
	@echo "  check              run django production checks"
	@echo "  clean              clean the project"
	@echo
	@echo "  docker-build       dockerise the project"
	@echo "  docker-migrate     dockerised version of migrate"
	@echo "  docker-run         dockerised version of run"
	@echo "  docker-dev         dockerised version of dev"
	@echo "  docker-check       dockerised version of check"
	@echo "  docker-up          docker-compose up"

label = Backend

section:
	@printf "\n[\e[94m\e[1m$(label)\e[0m]: \e[93m\e[1m$(tag)\e[0m\n"

# =========================================================================	#
# LOCAL                                                                     #
# =========================================================================	#

DATA_DIR = "./data"

migrate:
	@make section tag="Local - Migrating Database"
	python manage.py makemigrations
	@make section tag="Local - Making Migrations"
	python manage.py migrate

run: migrate
	@make section tag="Local - Serving"
	DEBUG="false" python manage.py runserver

dev: migrate
	@make section tag="Local - Serving (Dev Mode)"
	DEBUG="true" python manage.py runserver

check:
	@make section tag="Local - Performing Checks"
	python manage.py check --deploy

clean:
	@make section tag="Cleaning"
	make -C $(DATA_DIR) clean-data

# =========================================================================	#
# DOCKER                                                                    #
# =========================================================================	#

CONTAINER_NAME = dashboard-backend-server
IMAGE_NAME     = dashboard-backend
DIR_VOL        = $(shell pwd)/data
DIR_MNT        = /usr/src/dashboard-backend/data
MIGRATIONS_VOL = $(shell pwd)/dashboard/apps/dashboard_api/migrations
MIGRATIONS_MNT = /usr/src/dashboard-backend/dashboard/apps/dashboard_api/migrations
RUN_PARAMS     = --rm -v "$(DIR_VOL):$(DIR_MNT)" -v "$(MIGRATIONS_VOL):$(MIGRATIONS_MNT)" --name "$(CONTAINER_NAME)"

docker-build:
	@make section tag="Docker - Building Image"
	docker build -t "$(IMAGE_NAME)" ./

docker-migrate: docker-build
	@make section tag="Docker - Making Migrations"
	docker run $(RUN_PARAMS) $(IMAGE_NAME) makemigrations
	@make section tag="Docker - Migrating Database"
	docker run $(RUN_PARAMS) $(IMAGE_NAME) migrate

docker-run: docker-migrate
	@make section tag="Docker - Serving"
	docker run $(RUN_PARAMS) -p "8000:8000" $(IMAGE_NAME)

docker-dev: docker-migrate
	@make section tag="Docker - Serving (Dev Mode)"
	@echo NOT IMPLEMENTED

docker-check: docker-build
	@make section tag="Docker - Performing Checks"
	docker run $(RUN_PARAMS) $(IMAGE_NAME) check --deploy

docker-up:
	@make section tag="Docker Compose - Up"
	docker-compose up
