from flask_restful import (abort)


def validate_data(user):
    error_msg = []
    if "email" not in user:
        error_msg.append("email must be provided")
    if "provider" not in user:
        error_msg.append("social login provider must be provided")
    if "token" not in user:
        error_msg.append("token must be provided")
    return error_msg


def process_social_login(user):
    msg = validate_data(user)
    if len(msg) > 0:
        abort(403, message=msg)

    user_dict = {
        "email": user["email"], "id": user["id"],
        "provider": user["provider"], "first_name": None,
        "last_name": None
    }

    if "name" in user:
        if " " in user['name']:
            names = user['name'].split(' ')
            user_dict["first_name"] = names[0]
            user_dict["last_name"] = names[1]
        else:
            user_dict["first_name"] = user['name']

    print('lookup: {}'.format(user['email']))
# other fields
#    id :
#    full name:
#    email
#    provider
#    token
#


def process_social_logout(user):
    print(user)
