import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType
from helpers import utils
from database import db
from classes.location.model import Location as LocationModel
from classes.state_province.schema import check_state_province

__all__ = ['CreateLocation', 'DeleteLocation', 'UpdateLocation']


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

    def mutate(self, info, input_value):
        data = utils.input_to_dictionary(input_value)
        state_data = {'name': input['state_province']}
        state_province = check_state_province(state_data)
        data['state_province'] = state_province

        return CreateLocation(Location=check_location(data))


class UpdateLocationInput(graphene.InputObjectType,
                          LocationAttribute):
    id = graphene.ID(required=True,
                     description="Global Id of the Location.")


class UpdateLocation(graphene.Mutation):
    Location = graphene.Field(lambda: Location,
                    description="Location updated by this mutation.")

    class Arguments:
        input = UpdateLocationInput(required=True)

    def mutate(self, info, input_value):
        data = utils.input_to_dictionary(input_value)

        location = db.session.query(LocationModel).\
            filter_by(id=data['id'])
        location.update(data)
        db.session.commit()
        location = db.session.query(LocationModel).\
            filter_by(id=data['id']).first()

        return UpdateLocation(Location=location)


class DeleteLocation(graphene.Mutation):
    ok = graphene.Boolean()

    class Arguments:
        input = UpdateLocationInput(required=True)

    def mutate(self, info, input_value):
        data = utils.input_to_dictionary(input_value)

        location = db.session.query(LocationModel).filter_by(id=data['id'])
        location.delete()
        db.session.commit()

        return DeleteLocation(ok=True)
