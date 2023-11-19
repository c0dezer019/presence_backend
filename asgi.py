import uvicorn
from asgiref.wsgi import WsgiToAsgi

from core import create_app

def create_asgi():
    flask_app = create_app()
    asgi_app = WsgiToAsgi(flask_app)

    return asgi_app