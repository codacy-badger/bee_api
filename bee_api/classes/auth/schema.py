import graphene
from helpers import utils
from graphene_sqlalchemy import SQLAlchemyObjectType
from graphene import relay
from classes.user.model import User as UserModel
from app import db


def check_user(data):
    return true


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

    def mutate(self, info, input):
        data = utils.input_to_dictionary(input)
        user = UserModel()
        user.email = data['email']
        user.password = data['password']
        id = user.get_id
        methodList = [method for method in dir(UserModel) if callable(getattr(UserModel, method))]
        print(methodList)
        return CheckAuth(Auth=Auth)
