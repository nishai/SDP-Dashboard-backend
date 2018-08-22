
# ============= #
# BASE IMAGE:   #
# ============= #

FROM python:3.7-alpine

# ============= #
# WORKDIR:      #
# ============= #

# same as bash's cd
WORKDIR /usr/src/dashboard-backend
# mount point for data
VOLUME ["/usr/src/dashboard-backend/data"]
# mount point for migrations (alreafy copied by default, use this to override/save new migrations)
VOLUME ["/usr/src/dashboard-backend/dashboard/apps/dashboard_api/migrations"]

# ============= #
# DEPENDENCIES: #
# ============= #

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# ============= #
# CONFIG:       #
# ============= #

# documentation only
EXPOSE 8000
# binary to run
ENTRYPOINT [ "python", "manage.py" ]
# default arguments to entrypoint - mac needs 0.0.0.0 when used inside docker container
CMD [ "runserver", "0.0.0.0:8000" ]

# ============= #
# FILES:        #
# ============= #

# Make sure to add exceptions for files that can be copied in .dockerignore
COPY . .
