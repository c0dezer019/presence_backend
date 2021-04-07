# ComBot Server

Maintains the backend for the CommunityBot Discord Bot.

### Technology Used

- psycopg2 as a PostgreSQL adapter for Python.
- Flask for the framework.
- SQLAlchemy as a database engine.
- Flask-SQLAlchemy for less boilerplate setup.
- Pipenv for the Virtual Environment.
- Jsonify to turn things into JSON.
- pytz for managing timestamps.
- requests for handling requests from bot API.
- wheel for production build.
- mod_wsgi for the hosting service.

### Models

The bot requires two models. The Server and the User with a many-to-many relationship. A server has many users, and a
user has many servers. The database only tracks username with discriminator, Discord ID, last activity type, location,
and timestamp.