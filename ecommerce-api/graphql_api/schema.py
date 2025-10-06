from .queries import Query
import strawberry
from .mutations import Mutation

schema = strawberry.Schema(query=Query,mutation=Mutation)