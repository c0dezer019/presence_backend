from dotenv import load_dotenv
from pathlib import Path
import os


mode = 'development'

env_path = Path('.', '.env')
load_dotenv(dotenv_path = env_path)

# DB = os.getenv('DB') if mode == 'development' else os.getenv('CP_DB')
# USER = os.getenv('USER') if mode == 'development' else os.getenv('CP_USER')
# PASS = os.getenv('PASS') if mode == 'development' else os.getenv('CP_PASS')
# HOST = os.getenv('HOST') if mode == 'development' else os.getenv('CP_HOST')
# PORT = os.getenv('PORT')

# Index 0: development mode, 1: production
environment = [
    dict(
        DB = os.getenv('DB'),
        USER = os.getenv('USER'),
        PASS = os.getenv('PASS'),
        HOST = os.getenv('HOST'),
        PORT = os.getenv('PORT')
    ),
    dict(
        DB = os.getenv('CP_DB'),
        USER = os.getenv('CP_USER'),
        PASS = os.getenv('CP_PASS'),
        HOST = os.getenv('CP_HOST'),
        PORT = os.getenv('PORT'),
    ),
]
