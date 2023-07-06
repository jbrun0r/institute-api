from ..config import app_config
from .api_error import APIError
from ..model.user import Profile, User

from datetime import datetime, timedelta
from functools import wraps

import jwt
from flask import request

_secret_key = app_config.SECRET_KEY

_INSTITUTE = Profile.INSTITUTE.value
_EMPLOYEE = Profile.EMPLOYEE.value
_STUDENT = Profile.STUDENT.value

Auth = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    },
}


def generate_auth_token(expiration_time: timedelta, subject: int) -> str:
    """
    Generates an authentication token.

    Args:
        expiration_time (timedelta): The expiration time for the token.
        subject (int): The subject of the token.

    Returns:
        str: The generated authentication token.
    """
    payload_data = {
        "exp": datetime.utcnow() + expiration_time,
        "iat": datetime.utcnow(),
        "sub": subject,
    }
    return jwt.encode(payload_data, _secret_key, algorithm="HS256")


def decode_auth_token(auth_token: str) -> "dict[str, timedelta|int]":
    """
    Decodes an authentication token.

    Args:
        auth_token (str): The authentication token to decode.

    Returns:
        dict[str, timedelta|int]: The decoded token data.
    """
    try:
        return jwt.decode(auth_token, _secret_key, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise APIError("Expired login Token.", code=401, api_code="EXPIRED_TOKEN")
    except jwt.InvalidTokenError:
        raise APIError("Invalid login Token.", code=401, api_code="INVALID_TOKEN")


def get_user_from_token(jwt_token: str) -> User:
    """
    Retrieves the user from the provided JWT token.

    Args:
        jwt_token (str): The JWT token.

    Returns:
        User: The user associated with the token.

    Raises:
        APIError: If the decoded token does not refer to a user.
    """
    user_id = decode_auth_token(jwt_token)["sub"]
    if user := User.query.filter_by(id=user_id).first():
        return user
    raise APIError("Decoded token does not refer to a user.", code=404, api_code="DECODED_USER_NOT_FOUND")


def require_token(f):
    """
    Decorator to require a valid JWT token for accessing a route.

    Args:
        f (function): The route handler function.

    Returns:
        function: The decorated function.

    Raises:
        APIError: If the token is missing.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if token := request.headers.get("Authorization", default=None):
            decode_auth_token(token)
            return f(*args, **kwargs)
        raise APIError("Token is missing.", code=401, api_code="TOKEN_IS_MISSING")
    return decorated


def restrict_resource_to_profiles(*user_profiles, get_user: bool = True):
    """
    Decorator to restrict access to an API route based on user profiles.

    The route must also require a JWT token to identify the user.

    Args:
        *user_profiles: The profiles allowed to access the resource.
        get_user (bool, optional): Whether to include the user object in kwargs. Defaults to True.

    Returns:
        function: The decorator function.

    Raises:
        ValueError: If no user profile is provided or if an invalid profile is specified.
        APIError: If the token is missing or the user profile is not allowed to access the resource.
    """
    if len(user_profiles) == 0:
        raise ValueError(f"{restrict_resource_to_profiles.__name__} must have at least one argument")
    for profile in user_profiles:
        if profile not in Profile._member_names_:
            raise ValueError(f"Value '{profile}' is not a valid Profile")

    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            if token := request.headers.get("Authorization", default=None):
                user = get_user_from_token(token)
                if user.profile.value in user_profiles:
                    if get_user:
                        kwargs["user"] = user
                    return func(*args, **kwargs)
                raise APIError(f"{user.profile} cannot access resource limited to {user_profiles}", code=403, api_code="PROFILE_FORBIDDEN_ACCESS")
            raise APIError("Token is missing.", code=401, api_code="TOKEN_IS_MISSING")
        return decorated_function
    return decorator
