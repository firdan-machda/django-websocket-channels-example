import graphene
from graph.query import Query
from graph.mutation import Mutation
from graph.subscription import Subscription
import channels_graphql_ws

schema = graphene.Schema(
    query=Query,
    mutation=Mutation,
    subscription=Subscription
)

class MyGraphqlWsConsumer(channels_graphql_ws.GraphqlWsConsumer):
    """Channels WebSocket consumer which provides GraphQL API."""
    schema = schema

    # Uncomment to send keepalive message every 42 seconds.
    # send_keepalive_every = 42

    # Uncomment to process requests sequentially (useful for tests).
    # strict_ordering = True

    async def on_connect(self, payload):
        """New client connection handler."""
        # You can `raise` from here to reject the connection.
        print("New client connected!")