import graphene
from graph.query import Query
from graph.mutation import Mutation

schema = graphene.Schema(
    query=Query,
    mutation=Mutation,
)