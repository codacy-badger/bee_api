from flask import jsonify
from flask_graphql import GraphQLView
from flask_security \
    import (login_required, auth_token_required,
            http_auth_required)
from bee_api.app import (app, api)
from bee_api.schema import schema
from bee_api.classes.user.resource import (UserListResource, UserResource,
                                           RoleListResource, RoleResource)


def graphql_token_view():
    view = GraphQLView.as_view('graphql', schema=schema,
                               graphiql=bool(app.config.get("DEBUG", False)))
    view = auth_token_required(view)
    return view


app.add_url_rule('/graphql', view_func=graphql_token_view())


# Routes
@app.route('/')
def index():
    return jsonify({'message': 'Login required'})


@app.route('/token')
@auth_token_required
def token():
    return jsonify({'message': 'Token required'})


@app.route('/http')
@http_auth_required
def http():
    return jsonify({'message': 'HTTP required'})


api.add_resource(UserListResource, '/admin/users/')
api.add_resource(UserResource, '/admin/users/<int:id>')
api.add_resource(RoleListResource, '/admin/roles/')
api.add_resource(RoleResource, '/admin/roles/<int:id>')