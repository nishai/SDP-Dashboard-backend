
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

deploy:
	make -C $(DEPLOY_DIR) run
