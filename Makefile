
DEPLOY_DIR = "./deploy"

all:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  run        to run the project"
	@echo "  deploy     to deploy the project using docker"
	@echo "  clean      to clean all generated data"

migrate:
	python manage.py migrate

run:
	python manage.py runserver

clean-data:
	make -C $(DEPLOY_DIR) clean-data

clean:
	make -C $(DEPLOY_DIR) clean

#deploy:
#	make -C $(DEPLOY_DIR) run

docker-build:
	@echo
	@echo "Building Docker Container: dashboard-api"
	@echo "========================================"
	docker build -t dashboard-api ./

docker-migrate: docker-build
	@echo
	@echo "Migrating Docker Container:  dashboard-api"
	@echo "========================================"
	docker run --rm -it -v "$(shell pwd)/deploy/data:/usr/src/dashboard-backend/deploy/data" --name "dashboard-api-server" dashboard-api migrate

docker-run: docker-migrate
	@echo
	@echo "Running Docker Container:  dashboard-api"
	@echo "========================================"
	docker run --rm -it -v "$(shell pwd)/deploy/data:/usr/src/dashboard-backend/deploy/data" -p 8000:8000 --name "dashboard-api-server" dashboard-api
