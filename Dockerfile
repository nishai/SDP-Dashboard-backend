# ============= #
# dashboard     #
# ============= #

FROM python:3.7 as dashboard

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
RUN apt-get install make gcc linux-headers musl-dev openldap-dev && \
    pip install --no-cache-dir -r requirements.txt

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
