import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType
from bee_api.helpers import utils
from bee_api.database import db
from bee_api.classes.location.model import Location as LocationModel
from bee_api.classes.state_province.schema import check_state_province


def check_location(data):
    result = db.session.query(LocationModel). \
        filter_by(street_address=data['street_address'],
                  city=data['city']).first()
    if result is None:
        result = LocationModel(**data)
        db.session.add(result)
        db.session.commit()
    return result


class LocationAttribute:
    street_address = graphene.String(description="Street Address")
    city = graphene.String(description="City Location")
    postal_code = graphene.String(description="Zip or Postal Code")
    state_province = graphene.String(description="Name of state, province, ")


class Location(SQLAlchemyObjectType):
    class Meta:
        model = LocationModel
        interfaces = (relay.Node, )


class CreateLocationInput(graphene.InputObjectType,
                          LocationAttribute):
    pass


class CreateLocation(graphene.Mutation):
    Location = graphene.Field(lambda: Location,
                description="StateProvince created by this mutation.")

    class Arguments:
        input = CreateLocationInput(required=True)

    def mutate(self, info, input):
        data = utils.input_to_dictionary(input)
        state_data = {'name': input['state_province']}
        state_province = check_state_province(state_data)
        data['state_province'] = state_province
        Location = check_location(data)

        return CreateLocation(Location=Location)


class UpdateLocationInput(graphene.InputObjectType,
                          LocationAttribute):
    id = graphene.ID(required=True,
                     description="Global Id of the Location.")


class UpdateLocation(graphene.Mutation):
    Location = graphene.Field(lambda: Location,
                    description="Location updated by this mutation.")

    class Arguments:
        input = UpdateLocationInput(required=True)

    def mutate(self, info, input):
        data = utils.input_to_dictionary(input)

        Location = db.session.query(LocationModel).\
            filter_by(id=data['id'])
        Location.update(data)
        db.session.commit()
        Location = db.session.query(LocationModel).\
            filter_by(id=data['id']).first()

        return UpdateLocation(Location=Location)
