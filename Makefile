
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
TEST_IMAGE_NAME       = test-backend-image
TEST_CNTNR_NAME       = test-backend-container

VBIND_STATIC     = -v "$(shell pwd)/static:/app/static" -v "$(shell pwd)/dashboard/static:/app/dashboard/static"
VBIND_DATA       = -v "$(shell pwd)/data:/app/data"
VBIND_SRC        = -v "$(shell pwd)/manage.py:/app/manage.py" -v "$(shell pwd)/dashboard:/app/dashboard"
VBIND_TEST       = -v "$(shell pwd)/dashboard/apps/excel_import/excel_files/test_excels:/app/dashboard/apps/excel_import/excel_files/test_excels:ro" -v "$(shell pwd)/.git:/app/.git:ro"

RUN_FLAGS        = --rm --name "$(CNTNR_NAME)" $(VBIND_DATA) $(VBIND_SRC) $(VBIND_STATIC)

TEST_FLAGS       = --name "$(TEST_CNTNR_NAME)" $(VBIND_TEST)

dockerfile:
	@make section tag="Local - Building Dockerfile"
	docker build -t "$(IMAGE_NAME)" ./

docker-migrate: dockerfile
	@make section tag="Docker - Making Migrations"
	docker run $(RUN_FLAGS) $(IMAGE_NAME) makemigrations
	@make section tag="Docker - Migrating Database"
	docker run $(RUN_FLAGS) $(IMAGE_NAME) migrate
	docker run $(RUN_FLAGS) $(IMAGE_NAME) showmigrations

docker-dev: docker-migrate
	@make section tag="Docker - Serving (Dev Mode)"
	docker run $(RUN_FLAGS) -p 8000:8000 $(IMAGE_NAME) runserver 0.0.0.0:8000

docker-import: docker-migrate 
	@make section tag="Docker - Import Excel Files (Dev Mode)"
	docker run $(RUN_FLAGS) -p 8000:8000 $(IMAGE_NAME) excel_import --file=$(FILE)

docker-test: 
	@make section tag="Local - Building Dockerfile with --no-cache (Dev Mode)"
	docker build --no-cache -t "$(TEST_IMAGE_NAME)" ./
	@make section tag="Docker - Run Unit Tests (Dev Mode)"
	docker run $(TEST_FLAGS) $(ci_env) -p 8000:8000 --entrypoint pytest $(TEST_IMAGE_NAME) -v --cov=./
	@make section tag="Docker - Code Covergae (Dev Mode)"
	docker container start $(TEST_CNTNR_NAME)
	docker exec $(TEST_CNTNR_NAME) coverage xml
	docker cp $(TEST_CNTNR_NAME):/app/coverage.xml $(shell pwd)
	docker container stop $(TEST_CNTNR_NAME)
	@make section tag="Docker - Remove Containers and Images (Dev Mode)"
	docker rm $(TEST_CNTNR_NAME)
	docker rmi $(TEST_IMAGE_NAME)

# =========================================================================	#
# DOCKER - Serve Production                                                 #
# =========================================================================	#

IMAGE_NAME_SERVE = backend-image-serve

CNTNR_NAME_SERVE = backend-container-serve

VBIND_LOGS       = -v "$(shell pwd)/dashboard/logs:/app/dashboard/logs"
VBIND_DB         = -v "$(shell pwd)/data/db.sqlite3:/app/data/db.sqlite3"

RUN_FLAGS_SERVE  = --rm --name "$(CNTNR_NAME_SERVE)" $(VBIND_LOGS) $(VBIND_DB) $(VBIND_STATIC)

dockerfile.serve:
	@make section tag="Local - Building Dockerfile.serve"
	docker build -t "$(IMAGE_NAME_SERVE)" -f "Dockerfile.serve" ./

docker-serve: dockerfile.serve
	@make section tag="Docker - Serving"
	docker run $(RUN_FLAGS_SERVE) -p "8000:8000" $(IMAGE_NAME_SERVE)

