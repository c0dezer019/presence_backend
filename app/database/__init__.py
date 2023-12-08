from .database import Base, LocalSession

Session = LocalSession()
engine = Session.engine
