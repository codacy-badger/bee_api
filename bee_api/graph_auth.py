import graphene
from flask_graphql import GraphQLView
from app import app
from flask_graphql_auth import (AuthInfoField, GraphQLAuth, get_jwt_identity,
                                get_raw_jwt, create_access_token, create_refresh_token,
                                query_jwt_required, mutation_jwt_refresh_token_required,
                                mutation_jwt_required)

auth = GraphQLAuth(app)
user_claims = {"message": "VERI TAS LUX MEA"}


class MessageField(graphene.ObjectType):
    message = graphene.String()


class ProtectedUnion(graphene.Union):
    class Meta:
        types = (MessageField, AuthInfoField)

    @classmethod
    def resolve_type(cls, instance, info):
        return type(instance)


class AuthMutation(graphene.Mutation):
    class Arguments(object):
        username = graphene.String()
        password = graphene.String()

    access_token = graphene.String()
    refresh_token = graphene.String()

    @classmethod
    def mutate(cls, _, info, username, password):
        return AuthMutation(access_token=create_access_token(username, user_claims=user_claims),
                            refresh_token=create_refresh_token(username, user_claims=user_claims))


class ProtectedMutation(graphene.Mutation):
    class Arguments(object):
        token = graphene.String()

    message = graphene.Field(ProtectedUnion)

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info):
        return ProtectedMutation(message=MessageField(message="Protected mutation works"))


class RefreshMutation(graphene.Mutation):
    class Arguments(object):
        token = graphene.String()

    new_token = graphene.String()

    @classmethod
    @mutation_jwt_refresh_token_required
    def mutate(self, _, info):
        current_user = get_jwt_identity()
        return RefreshMutation(new_token=create_access_token(identity=current_user, user_claims=user_claims))


class Mutation(graphene.ObjectType):
    auth = AuthMutation.Field()
    refresh = RefreshMutation.Field()
    protected = ProtectedMutation.Field()


class Query(graphene.ObjectType):
    protected = graphene.Field(type=ProtectedUnion,
                               message=graphene.String(),
                               token=graphene.String())

    @query_jwt_required
    def resolve_protected(self, info, message):
        return MessageField(message=str(get_raw_jwt()))
