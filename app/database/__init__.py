from app.database.database import Database

database = Database()
engine = database.engine
session = database.session
