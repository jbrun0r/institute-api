from flask import request
from flask_restx import Resource

from ..dto.auth_dto import AuthenticationDTO
from ..dto.user_dto import UserDTO
from ..service.auth_service import login, activate_user, validate_email
from ..service.user_service import (
    generate_reset_password_email,
    reset_password,
    update_user_password,
)
from ..util.auth_utils import restrict_resource_to_profiles, _INSTITUTE, _EMPLOYEE, _STUDENT


api = AuthenticationDTO.api
_login = AuthenticationDTO.login
_login_response = AuthenticationDTO.login_response
_parser = AuthenticationDTO.parser
_set_password = AuthenticationDTO.set_password
_update_password = AuthenticationDTO.update_password
_reset_password_parser = AuthenticationDTO.reset_password_parser
_user_email = UserDTO.user_email

@api.route("/login")
class Login(Resource):
    """Endpoint for user login."""

    @api.doc(responses={
        400: "`USER_NOT_ACTIVATED` - User not activated.",
        401: "`FAILED_LOGIN` - Login failed.",
    })
    @api.expect(_login, validate=True)
    @api.marshal_with(_login_response, description="User logged in successfully.")
    def post(self):
        """Perform user login."""
        data = request.json
        return login(user_login=data), 200


@api.route("/password-update")
class UserPasswordResource(Resource):
    """Endpoint for updating user password."""

    @restrict_resource_to_profiles(_INSTITUTE, _EMPLOYEE, _STUDENT)
    @api.doc(
        "Update user password",
        responses={
            204: "User password updated successfully.",
            400: "`WRONG_CONFIRM_PASSWORD` - Incorrect password confirmation.",
            401: "`INVALID_TOKEN` `EXPIRED_TOKEN` `DECODED_USER_NOT_FOUND` `TOKEN_IS_MISSING` `WRONG_PASSWORD` - Authentication error.",
            403: "`PROFILE_FORBIDDEN_ACCESS` - Forbidden access for the profile.",
            404: "`USER_NOT_FOUND` - User not found.",
            422: "`WRONG_NEW_PASSWORD` - Invalid new password.",
        },
    )
    @api.expect(_update_password, _parser, validate=True)
    def put(self, user):
        """Update user password."""
        data = request.json
        return update_user_password(data, user), 204


@api.route("/activation/<string:token>")
@api.response(400, "`FAILED_DECODE` - Decoding failed.")
class ActivationResource(Resource):
    """Endpoint for user activation."""

    @api.doc(
        "Validate user email from a token",
        responses={
            204: "User email validated successfully.",
        },
    )
    def get(self, token):
        """Validate user email."""
        return validate_email(token), 204

    @api.doc(
        "Activate user from a token",
        responses={
            204: "User activated successfully.",
            404: "`EMAIL_NOT_FOUND` - Email not found.",
            409: "`USER_IS_ACTIVE` - User is already active.",
        },
    )
    @api.expect(_set_password, validate=True)
    def put(self, token):
        """Activate user."""
        data = request.json
        return activate_user(data, token), 204


@api.route("/forgot-password/")
@api.response(404, "`USER_NOT_FOUND` - User not found.")
class ForgotPasswordResource(Resource):
    """Endpoint for user password reset."""

    @api.doc(
        responses={
            204: "User email validated successfully.",
            400: "`FAILED_DECODE` - Decoding failed.",
        },
    )
    @api.expect(_reset_password_parser)
    def get(self):
        """Check if the reset password token is valid."""
        token = request.args["token"]
        return validate_email(token), 204

    @api.response(204, "Password reset email sent.")
    @api.expect(_user_email)
    def post(self):
        """Send reset password email."""
        data = request.json
        return generate_reset_password_email(data), 204

    @api.doc(
        "Update user's password",
        responses={
            204: "User's password updated successfully.",
            400: "`FAILED_DECODE` `WRONG_CONFIRM_PASSWORD` - Decoding failed or incorrect password confirmation.",
        },
    )
    @api.expect(_reset_password_parser, _set_password)
    def put(self):
        """Reset user's password."""
        data = request.json
        token = request.args["token"]
        return reset_password(data, token), 204
