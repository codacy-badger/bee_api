import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType
from bee_api.helpers import utils
from bee_api.database import db
from bee_api.classes.state_province.model \
    import StateProvince as StateProvinceModel
from bee_api.classes.country.schema import check_country


def check_state_province(data):
    result = db.session.query(StateProvinceModel). \
        filter_by(name=data['name']).first()
    if result is None:
        result = StateProvinceModel(**data)
        db.session.add(result)
        db.session.commit()
    return result


class StateProvinceAttribute:
    name = graphene.String(description="Name of the State, Province, "
                                       "or Region.")
    country = graphene.String(description="Assign State, Province, or "
                                          "Region to this Country.")


class StateProvince(SQLAlchemyObjectType):
    class Meta:
        model = StateProvinceModel
        interfaces = (relay.Node, )


class CreateStateProvinceInput(graphene.InputObjectType,
                               StateProvinceAttribute):
    pass


class CreateStateProvince(graphene.Mutation):
    StateProvince = graphene.Field(lambda: StateProvince,
                description="StateProvince created by this mutation.")

    class Arguments:
        input = CreateStateProvinceInput(required=True)

    def mutate(self, info, input):
        data = utils.input_to_dictionary(input)
        country_data = {'country': data['country']}
        country = check_country(country_data)
        StateProvince = check_state_province(data)

        return CreateStateProvince(StateProvince=StateProvince)


class UpdateStateProvinceInput(graphene.InputObjectType,
                               StateProvinceAttribute):
    id = graphene.ID(required=True,
                     description="Global Id of the StateProvince.")


class UpdateStateProvince(graphene.Mutation):
    StateProvince = graphene.Field(lambda: StateProvince,
                    description="StateProvince updated by this mutation.")

    class Arguments:
        input = UpdateStateProvinceInput(required=True)

    def mutate(self, info, input):
        data = utils.input_to_dictionary(input)

        StateProvince = db.session.query(StateProvinceModel).\
            filter_by(id=data['id'])
        StateProvince.update(data)
        db.session.commit()
        StateProvince = db.session.query(StateProvinceModel).\
            filter_by(id=data['id']).first()

        return UpdateStateProvince(StateProvince=StateProvince)
