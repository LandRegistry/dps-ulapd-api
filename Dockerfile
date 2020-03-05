# Set the base image to the base image
FROM hmlandregistry/dev_base_python_flask:5-3.6

# ---- Database stuff start
RUN yum install -y -q postgresql-devel

# Define all env vars in one layer, much quicker.
# SQL_HOST: THis must match the container name of the postgres commodity
# SQL_DATABASE: This must match the database created in postgres-init-fragment
# ALEMBIC_SQL_USERNAME: This is the root user specified in the postgres Dockerfile:
# SQL_USE_ALEMBIC_USER: (This will be temporarily overidden to yes when the alembic database upgrade is run)
# The following entries must match the user created in the fragments/postgres-init-fragment.sql:
# APP_SQL_USERNAME, SQL_PASSWORD (This will be temporarily overidden to be the root password when the alembic database upgrade is run)
ENV SQL_HOST=postgres \
 SQL_DATABASE=ulapd \
 ALEMBIC_SQL_USERNAME=root \
 SQL_USE_ALEMBIC_USER=no \
 APP_SQL_USERNAME=ulapd \
 SQL_PASSWORD=ulapd \
 SQLALCHEMY_POOL_RECYCLE="3300"

 USER root

# ---- Database stuff end

# ----
# Put your app-specific stuff here (extra yum installs etc).
# Any unique environment variables your config.py needs should also be added as ENV entries here

ENV APP_NAME="ulapd-api" \
 MAX_HEALTH_CASCADE="6" \
 LOG_LEVEL="DEBUG" \
 DEFAULT_TIMEOUT="30" \
 S3_BUCKET="PLACEHOLDER" \
 S3_BUCKET_RESTRICTED="PLACEHOLDER" \
 S3_BUCKET_REGION="PLACEHOLDER" \
 S3_URL_EXPIRATION="PLACEHOLDER" \
 ACCOUNT_API_URL="http://account-api:8080" \
 ACCOUNT_API_VERSION="v1" \
 VERIFICATION_API_URL="http://verification-api:8080" \
 VERIFICATION_API_VERSION="v1" \
 UPDATE_GROUPS_RETRY="3"

# ----

# The command to run the app is inherited from lr_base_python_flask

# Get the python environment ready.
# Have this at the end so if the files change, all the other steps don't need to be rerun. Same reason why _test is
# first. This ensures the container always has just what is in the requirements files as it will rerun this in a
# clean image.
ADD requirements_test.txt requirements_test.txt
ADD requirements.txt requirements.txt
RUN pip3 install -q -r requirements.txt && \
  pip3 install -q -r requirements_test.txt

# Copy default data scripts
ADD ./resources/data_scripts/load_default_data.sh /tmp/resources/scripts/
