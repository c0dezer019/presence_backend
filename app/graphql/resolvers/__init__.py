from app.database import database
from app.graphql.resolvers.resolver import Resolver

resolve = Resolver(database.session)
