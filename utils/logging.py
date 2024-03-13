from os import getenv
from os.path import relpath

from dotenv import load_dotenv

load_dotenv()


def rel(file: str) -> str:
    return relpath(file, getenv('START_PATH')).replace("/", ".")
