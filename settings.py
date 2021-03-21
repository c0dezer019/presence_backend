from dotenv import load_dotenv
from pathlib import Path
import os

# What config to use.
mode = 'testing'

env_path = Path('.', '.env')
load_dotenv(dotenv_path = env_path)

# Database configs
development = dict(
    DB = os.getenv('DB'),
    USER = os.getenv('USER'),
    PASS = os.getenv('PASS'),
    HOST = os.getenv('HOST'),
    PORT = os.getenv('PORT'),
)
testing = dict(
    USER = os.getenv('USER'),
    PASS = os.getenv('PASS'),
    HOST = os.getenv('HOST'),
    PORT = os.getenv('PORT'),
)
production = dict(
    DB = os.getenv('CP_DB'),
    USER = os.getenv('CP_USER'),
    PASS = os.getenv('CP_PASS'),
    HOST = os.getenv('CP_HOST'),
    PORT = os.getenv('PORT'),
)

# Packaging config dicts for easier importing and handling
env = {
    'development': development,
    'testing': testing,
    'production': production
}
