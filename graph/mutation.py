import graphene
import json
import graphql_jwt
from graphql.error import GraphQLError
from django.contrib.auth import get_user_model, authenticate, login
from webpush import send_user_notification
from webpush.forms import WebPushForm, SubscriptionForm


class SendNotificationMutation(graphene.Mutation):
    class Arguments:
        user_id=graphene.Int()
        head = graphene.String()
        body = graphene.String()
    status = graphene.Int()
    def mutate(self, info, user_id=None, head=None, body=None):
        User = get_user_model()
        try:
            user = User.objects.get(id=user_id)
            payload = { 'head': head, 'body': body}
            send_user_notification(user, payload, ttl=1000)
            return SendNotificationMutation(status=200)
        except User.DoesNotExist:
            return SendNotificationMutation(status=404)
        except TypeError:
            return SendNotificationMutation(status=500)


class SubscribeMutation(graphene.Mutation):
    """SubscribeMutation
    subscribe mutation obtained from django-webpush source code
    webpush/views.py/save_info
    """

    class Arguments:
        post_data = graphene.JSONString(required=True)
    
    status = graphene.Int()
    
    def mutate(self, info, post_data):
        subscription_data = post_data.pop("subscription", {})
        keys = subscription_data.pop("keys", {})
        subscription_data.update(keys)
        subscription_data["browser"] = post_data.pop("browser", None)
        subscription_data["user_agent"] = post_data.pop("user_agent", '')
        subscription_form = SubscriptionForm(subscription_data)
        # pass the data through WebPushForm for validation purpose
        web_push_form = WebPushForm(post_data)

        # Check if subscriptioninfo and the web push info bot are valid
        if subscription_form.is_valid() and web_push_form.is_valid():
            # Get the cleaned data in order to get status_type and group_name
            web_push_data = web_push_form.cleaned_data
            status_type = web_push_data.pop("status_type")
            group_name = web_push_data.pop("group")

            # We at least need the user or group to subscribe for a notification
            if info.context.user.is_authenticated or group_name:
                # Save the subscription info with subscription data
                # as the subscription data is a dictionary and its valid
                subscription = subscription_form.get_or_save()
                web_push_form.save_or_delete(
                    subscription=subscription, user=info.context.user,
                    status_type=status_type, group_name=group_name)

                # If subscribe is made, means object is created. So return 201
                if status_type == 'subscribe':
                    return SubscribeMutation(status=201)
                # Unsubscribe is made, means object is deleted. So return 202
                elif "unsubscribe":
                    return SubscribeMutation(status=202)

        return SubscribeMutation(status=400)


class Mutation(graphene.ObjectType):
    send_notification = SendNotificationMutation.Field()
    subscribe_push = SubscribeMutation.Field()
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
