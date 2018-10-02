import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyConnectionField
from bee_api.classes.country.schema \
    import (Country, CreateCountry, UpdateCountry)
from bee_api.classes.user.schema import (User)
from bee_api.classes.hive.schema import (Hive)
from bee_api.classes.state_province.schema \
    import (StateProvince, CreateStateProvince,  UpdateStateProvince)
from bee_api.classes.location.schema\
    import Location, CreateLocation, UpdateLocation


class Query(graphene.ObjectType):
    node = relay.Node.Field()
    stateProvinceList = SQLAlchemyConnectionField(StateProvince)
    countryList = SQLAlchemyConnectionField(Country)
    locationList = SQLAlchemyConnectionField(Location)
    userList = SQLAlchemyConnectionField(User)
    hivesList = SQLAlchemyConnectionField(Hive)


class Mutation(graphene.ObjectType):
    createCountry = CreateCountry.Field()
    updateCountry = UpdateCountry.Field()
    createStateProvince = CreateStateProvince.Field()
    updateStateProvince = UpdateStateProvince.Field()
    createLocation = CreateLocation.Field()
    updateLocation = UpdateLocation.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
