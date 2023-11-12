from asgiref.wsgi import WsgiToAsgi

from core import create_app

flask_app = create_app()

asgi_app = WsgiToAsgi(flask_app)