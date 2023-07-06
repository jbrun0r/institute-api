from .. import db
from ..util.api_error import APIError
from ..model import User
from ..service.email_service import send_email
from .auth_service import check_password, generate_hashed_password, generate_email_validation_token, decode_email_validation_token
from ..util.auth_utils import _INSTITUTE, _EMPLOYEE


def find_user_by(**user_attr) -> User:
    """
    Find a user by specified attributes.

    Args:
        **user_attr: User attributes to filter by.

    Returns:
        User: The found user.

    Raises:
        APIError: If the user is not found.
    """
    if user := User.query.filter_by(**user_attr).first():
        return user
    raise APIError(
        "User doesn't exist.",
        code=404,
        api_code="USER_NOT_FOUND",
        info=f"User not found by params {user_attr}",
    )


def save_new_user(data: dict, send_default_mail: bool = True, skip_commit: bool = False) -> User:
    """
    Save a new user.

    Args:
        data (dict): User data.
        send_default_mail (bool): Whether to send the default activation email.
        skip_commit (bool): Whether to skip committing to the database.

    Returns:
        User: The newly created user.

    Raises:
        APIError: If the user already exists.
    """
    if "profile" not in data:
        data["profile"] = _EMPLOYEE
    if User.query.filter_by(email=data["email"]).first():
        if user.activation_status:
            raise APIError("User already exists and is active.", code=409, api_code="USER_ALREADY_ACTIVE")
        else:
            raise APIError("User already exists.", code=409, api_code="USER_ALREADY_EXISTS")

    user = User(**data)
    if not skip_commit:
        db.session.add(user)
        db.session.commit()

    if send_default_mail:
        send_email(
            email=data["email"],
            template_name="USER_ACTIVATION.html",
            message_subject="Token User Activation",
            token_user_activation=f"{generate_email_validation_token(data['email'])}",
        )
    return user


def update_user(data: dict, user: User) -> User:
    """
    Update a user's information.

    Args:
        data (dict): Updated user data.
        user (User): The user to update.

    Returns:
        User: The updated user.
    """
    for attribute, new_value in data.items():
        setattr(user, attribute, new_value)
    db.session.commit()
    return user


def update_user_password(data: dict, user: User):
    """
    Update a user's password.

    Args:
        data (dict): Password update data.
        user (User): The user to update.

    Raises:
        APIError: If the password doesn't match or is invalid.
    """
    if data["new_password"] != data["confirm_password"]:
        raise APIError("Password doesn't match", code=400, api_code="WRONG_CONFIRM_PASSWORD")
    if not check_password(data["old_password"], user.password):
        raise APIError("Invalid password", code=401, api_code="WRONG_PASSWORD")
    if check_password(data["new_password"], user.password):
        raise APIError("New password cannot be the same as the current one", code=422, api_code="WRONG_NEW_PASSWORD")

    user.password = generate_hashed_password(data["new_password"])
    db.session.commit()


def deactivate_user(id: int, user_agent: User):
    """
    Deactivate a user.

    Args:
        id (int): The ID of the user to deactivate.
        user_agent (User): The user making the request.

    Raises:
        APIError: If the user is not allowed to deactivate the target user.
    """
    user_target = find_user_by(id=id)
    if (
        user_agent.id == user_target.id
        or (user_agent.profile == _INSTITUTE and user_agent.institute_id == user_target.institute_id)
    ):
        raise APIError("Cannot deactivate user.", code=403, api_code="DEACTIVATE_FORBIDDEN")
    user_target.activation_status = False
    db.session.commit()


def delete_user(user: User):
    """
    Delete a user from the database.

    Args:
        user (User): The user to delete.
    """
    if user.profile.value == _INSTITUTE:
        db.session.delete(user.employee.institute)
    db.session.delete(user)
    db.session.commit()


def generate_reset_password_email(data: dict):
    """
    Generate and send a reset password email.

    Args:
        data (dict): Email data.
    """
    if find_user_by(email=data["email"]):
        send_email(
            email=data["email"],
            template_name="RESET_PASSWORD.html",
            message_subject="Token Reset Password",
            token_reset_password=f"{generate_email_validation_token(data['email'])}",
        )


def reset_password(data: dict, token: str):
    """
    Reset a user's password.

    Args:
        data (dict): Password reset data.
        token (str): The reset password token.

    Raises:
        APIError: If the password doesn't match or the user is not found.
    """
    email = decode_email_validation_token(token)
    if data["password"] != data["confirm_password"]:
        raise APIError("Password doesn't match", code=400, api_code="WRONG_CONFIRM_PASSWORD")

    user = find_user_by(email=email)
    user.password = generate_hashed_password(data["password"])
    db.session.commit()
