# Standard modules

# Third party modules
from dotenv import load_dotenv
from fastapi import FastAPI
from pathlib import Path


env_path = Path("", "../.env")
load_dotenv(dotenv_path=env_path)


def create_app():
    fastapi = FastAPI(name=__name__)

    return fastapi
