# ============= #
# dashboard     #
# ============= #

FROM mysql:8 as dashboard

# same as bash's cd
WORKDIR /app

# dependencies file
COPY requirements.txt ./
# install dependencies
#   - behind a proxy pip and apk only requires (lowercase): http_proxy & https_proxy
#     set this with $ docker build --build-arg http_proxy="..." --build-arg https_proxy="..." ...
#   - *NB* apk does not work well when escape codes are used instead of special values
#     in the username and password, for example "%5C" instead of "\" does not work.

#RUN apt-get update && apt-get install -y python-dev libldap2-dev libsasl2-dev libssl-dev make && \

RUN \
        apt-get update

RUN \
        apt-get install -y \
        wget make gcc \
        libsasl2-dev libldap2-dev libssl-dev libffi-dev \
        build-essential checkinstall \
        libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev \
        libmysqlclient-dev

RUN \
        wget https://www.python.org/ftp/python/3.7.0/Python-3.7.0.tgz && \
        tar xzf Python-3.7.0.tgz && \
        cd Python-3.7.0 && \
        ./configure && \
        make altinstall && \
        cd .. && \
        ln -s /usr/local/bin/python3.7 /usr/local/bin/python3

RUN \
        wget https://bootstrap.pypa.io/get-pip.py && \
        python3.7 get-pip.py

RUN \
        pip install --no-cache-dir -r requirements.txt

RUN \
        mysql -u root -p password -e "CREATE DATABASE wits_dashboard;"

#RUN addgroup -g 1003 -S dockeruser && \
#	adduser -u 1003 -S -G dockeruser dockeruser 

# binary with args to run
ENTRYPOINT ["make"]
# aditional default arguments to entrypoint - macos needs 0.0.0.0 when used inside docker container
CMD ["dev"]

# Make sure to add exceptions for files that can be copied in .dockerignore
COPY . .

# RUN chown -R dockeruser:dockeruser .
# Switch to your new user in the docker image
#USER dockeruser

# set the DJANGO_DEVELOP environment variable inside the container
ENV DJANGO_DEVELOP "false"
