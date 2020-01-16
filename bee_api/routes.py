from flask import (jsonify, request)
from flask_graphql import GraphQLView
from werkzeug import secure_filename

from flask_security import (login_required, auth_token_required,
                            login_user, logout_user, http_auth_required)
from app import (app, api)
from schema import schema
from classes.user.resource import (UserListResource, UserResource,
                                           RoleListResource, RoleResource)
from classes.user.api import (process_social_login, process_social_logout)


def graphql_token_view():
    view = GraphQLView.as_view('graphql', schema=schema,
                               graphiql=bool(app.config.get("DEBUG", False)))
#    view = auth_token_required(view)
    return view


app.add_url_rule('/graphql', view_func=graphql_token_view())


# Routes
@app.route('/')
def index():
    return jsonify({'message': 'Login required'})


@app.route('/logout', methods=['GET', 'POST'])
#@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged Out'})


@app.route('/login', methods=['POST'])
def login():
    login_user()
    return jsonify({'message': 'Logged In'})


@app.route('/sociallogin', methods=['POST'])
def social_login():
    if 'user' in request.json:
        return process_social_login(request.json['user'])


@app.route('/sociallogout', methods=['POST'])
def social_logout():
    return process_social_logout(request.json)


@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        f.save(secure_filename(f.filename))
        return 'file uploaded successfully'


@app.route('/token')
@auth_token_required
def token():
    return jsonify({'message': 'Token required'})


@app.route('/http', methods=['GET', 'POST'])
@http_auth_required
def http():
    return jsonify({'message': 'HTTP required'})


#@app.route('/api')
#@login_manager.request_loader
#def load_user_from_request(request):

    # first, try to login using the api_key url arg
#    api_key = request.args.get('api_key')
#    if api_key:
#        user = User.query.filter_by(api_key=api_key).first()
#        if user:
#            return user

    # next, try to login using Basic Auth
#    api_key = request.headers.get('Authorization')
#    if api_key:
#        api_key = api_key.replace('Basic ', '', 1)
#        try:
#            api_key = base64.b64decode(api_key)
#        except TypeError:
#            pass
#        user = User.query.filter_by(api_key=api_key).first()
#        if user:
#            return user

    # finally, return None if both methods did not login the user
#    return None


#@roles_required('Administrator')
api.add_resource(UserListResource, '/admin/users/')
api.add_resource(UserResource, '/admin/users/<int:id>')
api.add_resource(RoleListResource, '/admin/roles/')
api.add_resource(RoleResource, '/admin/roles/<int:id>')
