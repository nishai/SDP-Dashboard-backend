
.DEFAULT_GOAL := help
# force rebuilds
.PHONY: dockerfile dockerfile.serve

# =========================================================================	#
# UTIL                                                                      #
# =========================================================================	#

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  migrate            initialise & migrate the database"
	@echo "  dev                serve the project in *develop mode*, supports live updates"
	@echo "  serve              serve the project in *production mode*"
	@echo
	@echo "  clean-data         clean the project data files"
	@echo "  clean-migrations   clean the project migration files"
	@echo "  clean              clean the project (both data and migration). Used for remaking database."
	@echo
	@echo "  dockerfile         dockerise the project"
	@echo "  docker-migrate     dockerised version of migrate"
	@echo "  docker-dev         dockerised version of dev"
	@echo "  docker-import      dockerised version for importing excel files"
	@echo "                     usage for all files: make docker-import"
	@echo "                     usage for specific file: make docker-import FILE-<filename>"
	@echo "  docker-test        runs `manage.py test` for running unit tests"
	@echo
	@echo "  dockerfile.serve   dockerise the production project"
	@echo "  docker-serve       dockerised version of serve"

label = Backend

section:
	@printf "\n[\e[94m\e[1m$(label)\e[0m]: \e[93m\e[1m$(tag)\e[0m\n"

# =========================================================================	#
# LOCAL                                                                     #
# =========================================================================	#

migrate:
	@make section tag="Local - Migrating Database"
	python manage.py makemigrations
	@make section tag="Local - Making Migrations"
	python manage.py migrate

dev: migrate
	@make section tag="Local - Serving (Dev Mode)"
	DEBUG="true" python manage.py runserver

serve: migrate
	@make section tag="Local - Serving"
	DEBUG="false" python manage.py runserver

clean-data:
	@make section tag="Cleaning Data"
	make -C "./data" clean-data

clean-migrations:
	@make section tag="Cleaning Migrations"
	make -C "./dashboard/apps/dashboard_api/migrations" clean-migrations

clean: clean-migrations clean-data

# =========================================================================	#
# DOCKER - Local Modifictions & Live Updates                                #
# =========================================================================	#

IMAGE_NAME       = backend-image
CNTNR_NAME       = backend-container

VBIND_DATA       = -v "$(shell pwd)/data:/app/data"
VBIND_SRC        = -v "$(shell pwd)/manage.py:/app/manage.py" -v "$(shell pwd)/dashboard:/app/dashboard"

RUN_FLAGS        = --rm --name "$(CNTNR_NAME)" $(VBIND_DATA) $(VBIND_SRC)

dockerfile:
	@make section tag="Local - Building Dockerfile"
	docker build -t "$(IMAGE_NAME)" ./

docker-migrate: dockerfile
	@make section tag="Docker - Making Migrations"
	docker run $(RUN_FLAGS) $(IMAGE_NAME) makemigrations
	@make section tag="Docker - Migrating Database"
	docker run $(RUN_FLAGS) $(IMAGE_NAME) migrate

docker-dev: docker-migrate
	@make section tag="Docker - Serving (Dev Mode)"
	docker run $(RUN_FLAGS) -p 8000:8000 $(IMAGE_NAME) runserver 0.0.0.0:8000

docker-import: docker-migrate 
	@make section tag="Docker - Import Excel Files (Dev Mode)"
	docker run $(RUN_FLAGS) -p 8000:8000 $(IMAGE_NAME) excel_import --file=$(FILE)

docker-test: docker-migrate 
	@make section tag="Docker - Run Unit Tests (Dev Mode)"
	docker run $(RUN_FLAGS) -p 8000:8000 $(IMAGE_NAME) test

# =========================================================================	#
# DOCKER - Serve Production                                                 #
# =========================================================================	#

IMAGE_NAME_SERVE = backend-image-serve

CNTNR_NAME_SERVE = backend-container-serve

RUN_FLAGS_SERVE  = --rm --name "$(CNTNR_NAME_SERVE)"

dockerfile.serve:
	@make section tag="Local - Building Dockerfile.serve"
	docker build -t "$(IMAGE_NAME_SERVE)" -f "Dockerfile.serve" ./

docker-serve: dockerfile.serve
	@make section tag="Docker - Serving"
	docker run $(RUN_FLAGS_SERVE) -p "8000:8000" $(IMAGE_NAME_SERVE)

