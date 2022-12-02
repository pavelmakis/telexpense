from os import environ
from pathlib import Path

BASE_DIR = Path(__file__).parent

# Bot configurations
API_TOKEN = environ["API_TOKEN"]
WEBAPP_HOST = environ["WEBAPP_HOST"]
WEBAPP_PORT = int(environ["WEBAPP_PORT"])
WEBHOOK_URL = environ["WEBHOOK_URL"]

# Sentry configurations
SENTRY_DSN = environ["SENTRY_DSN"]
ENVIRONMENT = environ["ENVIRONMENT"]
DEBUG = environ["DEBUG"]

# Database connection configuration
DB_HOST = environ["DB_HOST"]
DB_USER = environ["DB_USER"]
DB_PASSWORD = environ["DB_PASSWORD"]
DB_NAME = environ["DB_NAME"]
DB_PORT = int(environ["DB_PORT"])

# Redis storage configuration
REDIS_HOST = environ["REDIS_HOST"]
REDIS_PORT = int(environ["REDIS_PORT"])
REDIS_DB = int(environ["REDIS_DB"])

