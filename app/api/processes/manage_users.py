from firebase_admin import auth

from app.api.enums import AccessLevel


def update_user_permissions(email: str, access_level: AccessLevel):
    user = auth.get_user_by_email(email)
    auth.update_user(user.uid, custom_claims={"access_level": access_level.name})
    return True


def get_users():
    return [{'email': u.email,
             'uid': u.uid,
             'access_level': u.custom_claims.get('access_level')
             }
            for u in auth.list_users().users]


def delete_user(email):
    try:
        user = auth.get_user_by_email(email)
        auth.delete_user(user.uid)
        return f'Deleted user {user.email}'
    except Exception as e:
        raise e


def create_user(email, access_level):
    auth.update_user(auth.create_user(email=email).uid, custom_claims={"access_level": access_level.name})
    return True