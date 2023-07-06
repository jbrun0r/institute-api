from flask_restx import Namespace, fields

from .user_dto import UserDTO


PASSWORD_PATTERN = fields.String(
    required=True,
    description="User password",
    max_length=128,
    min_length=8,
    pattern=r"^(?=.*\d)(?=.*[A-Z])(?=.*[a-z])(?=.*[^\w\d\s:])([^\s]){8,128}$",
    example="@String0"
)


class AuthenticationDTO:
    api = Namespace("auth", description="Auth related operations")

    parser = api.parser().add_argument("Authorization", type=str, location="headers")

    reset_password_parser = api.parser().add_argument("token", required=True, type=str, location="query")

    login_response = api.model("LoginResponse", {
        "token": fields.String(required=True, description="User JWT"),
        "user": fields.Nested(model=UserDTO.user_auth),
    })

    login = api.model("Login", {
        **UserDTO.user_email,
        "password": PASSWORD_PATTERN,
    })

    update_password = api.model("UpdatePassword", {
        "old_password": PASSWORD_PATTERN,
        "new_password": PASSWORD_PATTERN,
        "confirm_password": PASSWORD_PATTERN,
    })

    set_password = api.model("SetPassword", {
        "password": PASSWORD_PATTERN,
        "confirm_password": PASSWORD_PATTERN,
    })
