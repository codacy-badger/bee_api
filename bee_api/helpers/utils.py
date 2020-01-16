from graphql_relay.node.node import from_global_id


def input_to_dictionary(input_value):
    """Method to convert Graphene inputs into dictionary"""
    dictionary = {}
    for key in input_value:
        # Convert GraphQL global id to database id
        if key[-2:] == 'id':
            input_value[key] = from_global_id(input_value[key])[1]
        dictionary[key] = input_value[key]
    return dictionary


# Custom validator
def must_not_be_blank(data):
    if not data:
        raise ValueError('Data not provided.')
