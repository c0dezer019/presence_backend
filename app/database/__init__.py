from .database import Base, LocalSession, TestSession as TestSes

Session = LocalSession()
dev_engine = Session.engine
TestSession = TestSes()
test_engine = TestSession.engine
