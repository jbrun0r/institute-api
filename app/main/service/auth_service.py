from .. import db
from ..config import app_config, Config
from ..util.api_error import APIError
from ..model import User
from ..util.auth_utils import generate_auth_token

from datetime import timedelta
from itsdangerous import (
    URLSafeTimedSerializer,
    BadData,
    SignatureExpired,
    BadTimeSignature,
    BadSignature,
    BadHeader,
)
import bcrypt
from typing import Dict, Any, Union


_jwt_exp = app_config.JWT_EXP
_activation_token_exp = app_config.ACTIVATION_EXP_DAYS


def generate_hashed_password(password: str) -> str:
    """Generate a hashed version of the password using bcrypt.

    Args:
        password (str): Password to be hashed.

    Returns:
        str: Hashed password.
    """
    password = password.encode("utf-8")
    return bcrypt.hashpw(password, bcrypt.gensalt()).decode("utf-8")


def check_password(password: str, hashed_password: str) -> bool:
    """Check if the provided password matches the hashed password.

    Args:
        password (str): Password to be checked.
        hashed_password (str): Hashed password to compare against.

    Returns:
        bool: True if the passwords match, False otherwise.
    """
    password = password.encode("utf-8")
    hashed_password = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password, hashed_password)


def login(user_login: Dict[str, Any]) -> Dict[str, Union[str, User]]:
    """Process the user login.

    Args:
        user_login (dict): User login data containing email and password.

    Returns:
        dict: Dictionary containing the JWT token and the user information.

    Raises:
        APIError: If the user is not found, the account is not activated, or the login credentials are incorrect.
    """
    if user := User.query.filter_by(email=user_login['email']).first():
        if not user.activation_status:
            raise APIError("User's account isn't active yet", code=400, api_code="USER_NOT_ACTIVATED")
        login_pwd = user_login["password"]
        user_pwd = user.password
        if check_password(login_pwd, user_pwd):
            jwt_token = generate_auth_token(timedelta(hours=_jwt_exp), user.id)
            user.token = jwt_token
            db.session.commit()
            return dict(token=jwt_token, user=user)
    raise APIError("Incorrect User or Password", code=401, api_code="FAILED_LOGIN")


def generate_email_validation_token(email: str) -> str:
    """Generate token for email validation.

    Args:
        email (str): Email to be encoded into the token.

    Returns:
        str: Generated token for email validation.
    """
    serializer = URLSafeTimedSerializer(Config.SECRET_KEY)
    return serializer.dumps(email, salt="email-confirm")


def decode_email_validation_token(token: str) -> str:
    """Decode the email validation token.

    Args:
        token (str): Token to be decoded.

    Returns:
        str: Decoded email from the token.

    Raises:
        APIError: If the token is invalid or expired.
    """
    serializer = URLSafeTimedSerializer(Config.SECRET_KEY)
    try:
        decoded_token = serializer.loads(
            token,
            salt="email-confirm",
            max_age=timedelta(days=_activation_token_exp).total_seconds(),
        )
    except (
        SignatureExpired,
        BadData,
        BadTimeSignature,
        BadSignature,
        BadHeader,
    ) as e:
        raise APIError("Invalid token to decode. Maybe expired.", code=400, api_code="FAILED_DECODE") from e

    return decoded_token


def validate_email(token: str) -> None:
    """Validate the email token.

    Args:
        token (str): Token to be validated.

    Raises:
        APIError: If the user doesn't exist.
    """
    decoded_token = decode_email_validation_token(token)
    if User.query.filter_by(email=decoded_token).first() is None:
        raise APIError("User doesn't exist.", code=404, api_code="USER_NOT_FOUND")



def activate_user(data: dict, token: str) -> None:
    """Activate the user's account.

    Args:
        data (dict): Data containing the password.
        token (str): Token for email validation.

    Raises:
        APIError: If the user with the email doesn't exist, or if the user is already active.
    """
    email = decode_email_validation_token(token)
    user = User.query.filter_by(email=email).first()

    if user is None:
        raise APIError("User with this email doesn't exist.", code=404, api_code="EMAIL_NOT_FOUND")

    if user.activation_status:
        raise APIError("User is already active.", code=409, api_code="USER_IS_ACTIVE")

    user.password = generate_hashed_password(data["password"])
    user.activation_status = True

    db.session.commit()
