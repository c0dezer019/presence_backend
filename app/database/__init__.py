from .database import Base, Database

database = Database()
engine = database.engine
