from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType
from bee_api.classes.hive.model import Hive as HiveModel
from bee_api.classes.hive.model import HiveData as HiveDataModel


class Hive(SQLAlchemyObjectType):
    class Meta:
        model = HiveModel
        interfaces = (relay.Node, )


class HiveData(SQLAlchemyObjectType):
    class Meta:
        model = HiveDataModel
        interfaces = (relay.Node, )