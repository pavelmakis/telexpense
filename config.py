from os import environ
from pathlib import Path

BASE_DIR = Path(__file__).parent

# Bot configurations
API_TOKEN = environ["API_TOKEN"]
# PAYMENTS_TOKEN = environ["PAYMENTS_TOKEN"]

WEBAPP_HOST = environ["WEBAPP_HOST"]
WEBAPP_PORT = int(environ["WEBAPP_PORT"])


# Webhook configurartion
WEBHOOK_HOST = environ["WEBHOOK_HOST"]
WEBHOOK_PATH = environ["WEBHOOK_PATH"]
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# Database connection configuration
DB_HOST = environ["DB_HOST"]
DB_USER = environ["DB_USER"]
DB_PASSWORD = environ["DB_PASSWORD"]
DB_NAME = environ["DB_NAME"]
DB_PORT = int(environ["DB_PORT"])

# Redis storage configuration
REDIS_STORAGE_HOST = environ["REDIS_HOST"]
REDIS_STORAGE_PORT = int(environ["REDIS_PORT"])
REDIS_STORAGE_DB = int(environ["REDIS_DB"])
