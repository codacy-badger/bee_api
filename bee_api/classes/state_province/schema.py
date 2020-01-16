import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType
from helpers import utils
from database import db
from classes.state_province.model \
    import StateProvince as StateProvinceModel
from classes.country.schema import check_country

__all__ = ['CreateStateProvince', 'UpdateStateProvince',
           'DeleteStateProvince', 'check_state_province']


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

    def mutate(self, info, input_value):
        data = utils.input_to_dictionary(input_value)

        return CreateStateProvince(StateProvince=check_state_province(data))


class UpdateStateProvinceInput(graphene.InputObjectType,
                               StateProvinceAttribute):
    id = graphene.ID(required=True,
                     description="Global Id of the StateProvince.")


class UpdateStateProvince(graphene.Mutation):
    StateProvince = graphene.Field(lambda: StateProvince,
                    description="StateProvince updated by this mutation.")

    class Arguments:
        input = UpdateStateProvinceInput(required=True)

    def mutate(self, info, input_value):
        data = utils.input_to_dictionary(input_value)

        state_province = db.session.query(StateProvinceModel).\
            filter_by(id=data['id'])
        state_province.update(data)
        db.session.commit()
        state_province = db.session.query(StateProvinceModel).\
            filter_by(id=data['id']).first()

        return UpdateStateProvince(StateProvince=state_province)


class DeleteStateProvince(graphene.Mutation):
    ok = graphene.Boolean()

    class Arguments:
        input = UpdateStateProvinceInput(required=True)

    def mutate(self, info, input_value):
        data = utils.input_to_dictionary(input_value)

        province = db.session.query(StateProvinceModel).filter_by(id=data['id'])
        province.delete()
        db.session.commit()

        return DeleteStateProvince(ok=True)
