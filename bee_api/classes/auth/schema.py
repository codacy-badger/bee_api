import graphene
from helpers import utils
from graphene_sqlalchemy import SQLAlchemyObjectType
from graphene import relay
from classes.user.model import User as UserModel

__all__ = ['Auth', 'AuthAttribute', 'CheckAuth', 'CheckAuthInput']


def check_user(data):
    return True


class AuthAttribute:
    email = graphene.String(description="Email")
    password = graphene.String(description="Password")


class Auth(SQLAlchemyObjectType):
    class Meta:
        model = UserModel
        interfaces = (relay.Node, )


class CheckAuthInput(graphene.InputObjectType, AuthAttribute):
    pass


class CheckAuth(graphene.Mutation):
    Auth = graphene.Field(lambda: Auth,
                          description="User created by this mutation.")

    class Arguments:
        input = CheckAuthInput(required=True)

    def mutate(self, info, input_value):
        data = utils.input_to_dictionary(input_value)
        user = UserModel()
        user.email = data['email']
        user.password = data['password']
        return CheckAuth(Auth=Auth)
