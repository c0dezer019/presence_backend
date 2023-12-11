from .database import Base, LocalSession

ORMSession = LocalSession()
engine = ORMSession.engine
