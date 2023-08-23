import graphene
from graph.subscription import MySubscription

class TestMutate(graphene.Mutation):
    status = graphene.Int()
    def mutate(self, info):
        MySubscription.broadcast() 
        print("gigachad")
    
class TestMutateBoss(graphene.ObjectType):
    test_mutate = TestMutate.Field()

class Mutation(TestMutateBoss, graphene.ObjectType):
    """Root GraphQL mutation."""
    # Check Graphene docs to see how to define mutations.
    pass
