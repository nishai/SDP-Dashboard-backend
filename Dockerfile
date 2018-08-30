
# To make use of caching make sure to add the changes from:
# ./Dockerfile to ./Dockerfile.serve

# ============= #
# django        #
# ============= #

FROM python:3.7-alpine

# set the debug environment variable inside the container
ENV DASHBOARD_DEVELOP "true"
ENV http_proxy "http://students%5C1501858:Hanoch%2E456@proxyss.wits.ac.za:80"
ENV https_proxy "https://students%5C1501858:Hanoch%2E456@proxyss.wits.ac.za:80"
ENV ftp_proxy "ftp://students%5C1501858:Hanoch%2E456@proxyss.wits.ac.za:80"
ENV HTTP_PROXY "http://students%5C1501858:Hanoch%2E456@proxyss.wits.ac.za:80"
ENV HTTPS_PROXY "https://students%5C1501858:Hanoch%2E456@proxyss.wits.ac.za:80"
ENV FTP_PROXY "ftp://students%5C1501858:Hanoch%2E456@proxyss.wits.ac.za:80"

# same as bash's cd
WORKDIR /app

# dependencies file
COPY requirements.txt ./
# install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# documentation only
EXPOSE 8000
# binary with args to run
ENTRYPOINT ["python", "manage.py"]
# aditional default arguments to entrypoint - macos needs 0.0.0.0 when used inside docker container
CMD ["runserver", "0.0.0.0:8000"]

# Make sure to add exceptions for files that can be copied in .dockerignore
COPY . .
