from app.database import db
from app.graphql.resolvers.resolver import Resolver

resolve = Resolver(db.session)
