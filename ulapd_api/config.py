import os

# RULES OF CONFIG:
# 1. No region specific code. Regions are defined by setting the OS environment variables appropriately to build up the
# desired behaviour.
# 2. No use of defaults when getting OS environment variables. They must all be set to the required values prior to the
# app starting.
# 3. This is the only file in the app where os.environ should be used.

# --- Database variables start

# These must all be set in the OS environment.
# The password must be the correct one for either the app user or alembic user,
# depending on which will be used (which is controlled by the SQL_USE_ALEMBIC_USER variable)

SQL_HOST = os.environ['SQL_HOST']
SQL_DATABASE = os.environ['SQL_DATABASE']
SQL_PASSWORD = os.environ['SQL_PASSWORD']
APP_SQL_USERNAME = os.environ['APP_SQL_USERNAME']
ALEMBIC_SQL_USERNAME = os.environ['ALEMBIC_SQL_USERNAME']

if os.environ['SQL_USE_ALEMBIC_USER'] == 'yes':
    FINAL_SQL_USERNAME = ALEMBIC_SQL_USERNAME
else:
    FINAL_SQL_USERNAME = APP_SQL_USERNAME

SQLALCHEMY_DATABASE_URI = 'postgres://{0}:{1}@{2}/{3}'.format(FINAL_SQL_USERNAME, SQL_PASSWORD, SQL_HOST, SQL_DATABASE)
SQLALCHEMY_TRACK_MODIFICATIONS = False  # Explicitly set this in order to remove warning on run
SQLALCHEMY_POOL_RECYCLE = int(os.environ['SQLALCHEMY_POOL_RECYCLE'])

# --- Database variables end

# For the enhanced logging extension
FLASK_LOG_LEVEL = os.environ['LOG_LEVEL']

# For S3 connections
S3_BUCKET = os.environ['S3_BUCKET']
S3_BUCKET_RESTRICTED = os.environ['S3_BUCKET_RESTRICTED']
S3_BUCKET_REGION = os.environ['S3_BUCKET_REGION']
S3_URL_EXPIRATION = int(os.environ['S3_URL_EXPIRATION'])

# Account-api
ACCOUNT_API_URL = os.environ['ACCOUNT_API_URL']
ACCOUNT_API_VERSION = os.environ['ACCOUNT_API_VERSION']
UPDATE_GROUPS_RETRY = os.environ['UPDATE_GROUPS_RETRY']

# Verification-api
VERIFICATION_API_URL = os.environ['VERIFICATION_API_URL']
VERIFICATION_API_VERSION = os.environ['VERIFICATION_API_VERSION']

# For health route
COMMIT = os.environ['COMMIT']

# This APP_NAME variable is to allow changing the app name when the app is running in a cluster. So that
# each app in the cluster will have a unique name.
APP_NAME = os.environ['APP_NAME']
MAX_HEALTH_CASCADE = int(os.environ['MAX_HEALTH_CASCADE'])
DEFAULT_TIMEOUT = int(os.environ['DEFAULT_TIMEOUT'])

# Following is an example of building the dependency structure used by the cascade route
# SELF can be used to demonstrate how it works (i.e. it will call it's own casecade
# route until MAX_HEALTH_CASCADE is hit)
# SELF = "http://localhost:8080"
# DEPENDENCIES = {"SELF": SELF}

DEPENDENCIES = {
    "Postgres": SQLALCHEMY_DATABASE_URI,
    "account-api": ACCOUNT_API_URL,
    "verification": VERIFICATION_API_URL
}
