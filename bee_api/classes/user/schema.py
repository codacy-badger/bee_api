from graphene_sqlalchemy import SQLAlchemyObjectType
from graphene import relay
from bee_api.classes.user.model import User as UserModel


class User(SQLAlchemyObjectType):
    class Meta:
        model = UserModel
        interfaces = (relay.Node, )
