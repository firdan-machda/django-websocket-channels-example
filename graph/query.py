import graphene

class Query(graphene.ObjectType):
    """Root GraphQL query."""
    # Graphene requires at least one field to be present. Check
    # Graphene docs to see how to define queries.
    value = graphene.String()
    async def resolve_value(self):
        return "test"