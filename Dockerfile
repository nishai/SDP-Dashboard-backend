
# To make use of caching make sure to add the changes from:
# ./Dockerfile to ./Dockerfile.serve

# ============= #
# common        #
# ============= #

FROM python:3.7-alpine as common

# same as bash's cd
WORKDIR /app

# dependencies file
COPY requirements.txt ./
# install dependencies
# behind a proxy pip only requires (lowercase): http_proxy & https_proxy
# set this with $ docker build --build-arg http_proxy="" --build-arg https_proxy="" ...
RUN pip install --no-cache-dir -r requirements.txt

# documentation only
EXPOSE 8000
# binary with args to run
ENTRYPOINT ["python", "manage.py"]
# aditional default arguments to entrypoint - macos needs 0.0.0.0 when used inside docker container
CMD ["runserver", "0.0.0.0:8000"]

# Make sure to add exceptions for files that can be copied in .dockerignore
COPY . .

# ============= #
# develop       #
# ============= #

FROM common as develop

# set the debug environment variable inside the container
ENV DASHBOARD_DEVELOP "true"
