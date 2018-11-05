.DEFAULT_GOAL := help
# force rebuilds
.PHONY: help FORCE

# =========================================================================	#
# UTIL                                                                      #
# =========================================================================	#

help:
	@echo "Please use 'make <target>' where <target> is one of"
	@echo "    migrate            initialise & migrate the database"
	@echo "    import             import an excel file into the db"
	@echo "                        to specify a file use the argument 'file=<file_url>'"
	@echo "    dev                serve the project in *develop mode*, supports live updates"
	@echo "    test               run project tests, and output coverage"
	@echo "    serve              serve the project in *production mode*"
	@echo
	@echo "    clean-data         clean the project data files"
	@echo "    clean-migrations   clean the project migration files"
	@echo "    clean-dist         clean the dist folder (rm)"
	@echo "    clean-logs         clean the logs folder of all logs"
	@echo "    clean-cov          clean the coverage folder (rm)"
	@echo "    clean-pycache      clean all the pycache files (rm)"
	@echo "    clean              clean everything except data"

# =========================================================================	#
# PRINT                                                                     #
# =========================================================================	#

label           := Backend
docker          := $(shell [ -f /.dockerenv ] && echo 1)
location        := $(if $(docker),\033[94mDocker\033[0m,\033[92mLocal\033[0m)

section:
	@printf "\n[\033[91m\033[1m$(label): $(location)\033[0m]: \033[93m\033[1m$(tag)\033[0m\n"
ifdef details
	@printf	"\033[90m$(details)\033[0m\n\n"
endif

# =========================================================================	#
# LOCAL                                                                     #
# =========================================================================	#

DEV_PORT        := 3000
PROD_PORT       := 4000

echo-dev-port:
	@echo $(DEV_PORT)
echo-prod-port:
	@echo $(PROD_PORT)

PY_ARGS         := -B # same as PYTHONDONTWRITEBYTECODE
ENV_DEV         := PYTHONDONTWRITEBYTECODE="true" DJANGO_DEVELOP="true"
ENV_PROD        := PYTHONDONTWRITEBYTECODE="true" DJANGO_DEVELOP="false"
ENV_TEST        := PYTHONDONTWRITEBYTECODE="true" DJANGO_DEVELOP="true" COVERAGE_FILE="coverage/coverage.dat"
OUT_COV_FILE    := coverage/coverage.xml

admin: migrate
	@make section tag="Local - Creating Default Admin User"
	$(ENV_DEV) python manage.py createsuperuser --username=admin --email=admin@dashboard-dev.ms.wits.ac.za || true

migrate:
	@make section tag="Making Migrations"
	$(ENV_DEV) python $(PY_ARGS) manage.py makemigrations
	@make section tag="Migrating Database"
	$(ENV_DEV) python $(PY_ARGS) manage.py migrate --run-syncdb

import: migrate
	@make section tag="Import Excel Files (Dev Mode)"
	$(ENV_DEV) python $(PY_ARGS) manage.py excel_import --file="$(file)"

dev: migrate
	@make section tag="Serving (Dev Mode)"
	$(ENV_DEV) python $(PY_ARGS) manage.py runserver 0.0.0.0:$(DEV_PORT)

test: clean clean-data migrate
	@mkdir -p coverage
	@make section tag="Run Unit Tests"
	$(ENV_TEST) python $(PY_ARGS) -m pytest -v --cov=./
	@make section tag="Code Covergage"
	$(ENV_TEST) python $(PY_ARGS) -m coverage xml -o $(OUT_COV_FILE)

dist: clean-dist
	@make section tag="Collecting Static Files"
	$(ENV_PROD) python $(PY_ARGS) manage.py collectstatic

serve: dist migrate
	@make section tag="Serving"
	$(ENV_PROD) python $(PY_ARGS) manage.py runserver 0.0.0.0:$(PROD_PORT)

# =========================================================================	#
# CLEAN                                                                     #
# =========================================================================	#

clean: clean-data clean-migrations

clean-data:
	@make section tag="Cleaning Data"
	make -C "./data" clean-data

clean-migrations:
	@make section tag="Cleaning Migrations"
	@#make -C "./dashboard/apps/dashboard_api/migrations" clean-migrations
	@find ./dashboard/apps/*/migrations/* -not -name "README.md" -a -not -name ".gitignore" -a -not -name "Makefile" -a -not -name "__init__.py" -print -exec rm -rf {} \; || true

clean-dist:
	@make section tag="Cleaning Dist Folder"
	rm -rf ./dist || true

clean-logs:
	@make section tag="Cleaning Logs"
	make -C "./logs" clean-logs

clean-cov:
	@make section tag="Cleaning Coverage"
	rm -rvf ./coverage ./.pytest_cache/ || true

clean-pycache:
	@make section tag="Cleaning all __pycache__"
	find . -name __pycache__ -exec rm -rf {} \; || true

clean: clean-dist clean-logs clean-cov clean-pycache

