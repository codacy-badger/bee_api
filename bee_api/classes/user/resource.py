from flask_restful import (reqparse, Resource, fields, marshal_with,
                           abort)
from flask_security.utils import hash_password
from flask_security import (login_required, current_user)
from bee_api.classes.user.model import (User, Role)
from bee_api.app import db

role_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'description': fields.String,
    'index': fields.String,
    'permissions': fields.Integer
}

user_fields = {
    'id': fields.Integer,
    'email': fields.String,
    'first_name': fields.String,
    'last_name': fields.String,
    'active': fields.Boolean,
    'confirmed_at': fields.DateTime,
    'last_login_at': fields.DateTime,
    'last_login_ip': fields.String,
    'current_login_at': fields.DateTime,
    'current_login_ip': fields.String,
    'registered_on': fields.DateTime,
    'login_count': fields.Integer,
    'roles': fields.List(fields.Nested(role_fields))
}

user_parse = reqparse.RequestParser()
user_parse.add_argument('email', type=str, location='json',
                        help='Email must be provided.', required=True)
user_parse.add_argument('password', type=str, location='json')
user_parse.add_argument('first_name', type=str, location='json')
user_parse.add_argument('last_name', type=str, location='json')
user_parse.add_argument('active', type=bool, location='json')
user_parse.add_argument('roles', type=list, location='json')


role_parse = reqparse.RequestParser()
role_parse.add_argument('name', type=str, location='json',
                        help='Role Name must be provided.', required=True)
role_parse.add_argument('description', type=str, location='json')
role_parse.add_argument('index', type=str, location='json')
role_parse.add_argument('default', type=bool, location='json')
role_parse.add_argument('permissions', type=int, location='json')


class UserResource(Resource):
    method_decorators = [login_required]

    @marshal_with(user_fields)
    def get(self, id):
        if current_user.id == id or \
                'Administrator' in current_user.roles:
            user = db.session.query(User).filter(User.id == id).first()
            if user:
                return user
            abort(404, message="User {} doesn't exist".format(id))
        abort(403, message="Account doesn't have access")

    def delete(self, id):
        user = db.session.query(User).filter(User.id == id).first()
# TODO: Need logic to remove user/role
        if not user:
            abort(404, message="User {} doesn't exist".format(id))
        db.session.delete(user)
        db.session.commit()
        return {}, 204

    @marshal_with(user_fields)
    def put(self, id):
        if current_user.id == id or \
                'Administrator' in current_user.roles:
            parsed_args = user_parse.parse_args()
            user = db.session.query(User).filter(User.id == id).first()
            if user:
                user.email = parsed_args['email']
                user.first_name = parsed_args['first_name']
                user.last_name = parsed_args['last_name']
                user.password = hash_password(parsed_args['password'])
                user.active = parsed_args['active']
# TODO: Need logic to modify user/role
                db.session.add(user)
                db.session.commit()
                return user, 201

        abort(403, message="Account doesn't have access")


class UserListResource(Resource):
    method_decorators = [login_required]

    @marshal_with(user_fields)
    def get(self):
        if 'Administrator' in current_user.roles:
            return db.session.query(User).all()
        abort(403, message="Account doesn't have access")

    @marshal_with(user_fields)
    def post(self):
        if 'Administrator' in current_user.roles:
            parsed_args = user_parse.parse_args()
            user = User(email=parsed_args['email'],
                        first_name=parsed_args['first_name'],
                        last_name=parsed_args['last_name'],
                        password=hash_password(parsed_args['password']),
                        roles=parsed_args['roles']
                        )
            db.session.add(user)
            db.session.commit()
            return user, 201

        abort(403, message="Account doesn't have access")


class RoleResource(Resource):
    method_decorators = [login_required]

    @marshal_with(role_fields)
    def get(self, id):
        if 'Administrator' in current_user.roles:
            role = db.session.query(Role).filter(Role.id == id).first()
            if role:
                return role
            abort(404, message="Role {} doesn't exist".format(id))
        abort(403, message="Account doesn't have access")

    def delete(self, id):
        role = db.session.query(Role).filter(Role.id == id).first()
        if not role:
            abort(404, message="Role {} doesn't exist".format(id))
        db.session.delete(role)
        db.session.commit()
        return {}, 204

    @marshal_with(role_fields)
    def put(self, id):
        if 'Administrator' in current_user.roles:
            parsed_args = role_parse.parse_args()
            role = db.session.query(Role).filter(Role.id == id).first()
            if role:
                role.name = parsed_args['name']
                role.description = parsed_args['description']
                role.index = parsed_args['index']
                role.default = hash_password(parsed_args['default'])
                role.permissions = parsed_args['permissions']
                # TODO: Need logic to modify role/role
                db.session.add(role)
                db.session.commit()
                return role, 201

        abort(403, message="Account doesn't have access")


class RoleListResource(Resource):
    method_decorators = [login_required]

    @marshal_with(role_fields)
    def get(self):
        if 'Administrator' in current_user.roles:
            return db.session.query(Role).all()
        abort(403, message="Account doesn't have access")

    @marshal_with(role_fields)
    def post(self):
        if 'Administrator' in current_user.roles:
            parsed_args = role_parse.parse_args()
            role = Role(name=parsed_args['name'],
                        description=parsed_args['description'],
                        index=parsed_args['index'],
                        default=hash_password(parsed_args['default']),
                        permissions=parsed_args['permissions']
                        )
            db.session.add(role)
            db.session.commit()
            return role, 201

        abort(403, message="Account doesn't have access")
