from flask import request
from flask_restx import Resource

from ..dto.auth_dto import AuthenticationDTO
from ..dto.user_dto import UserDTO
from ..service.user_service import (deactivate_user, delete_user,
                                    update_user,)
from ..util.auth_utils import restrict_resource_to_profiles, _INSTITUTE, _EMPLOYEE, _STUDENT

api = UserDTO.api
_parser = AuthenticationDTO.parser
_user = UserDTO.user
_user_get = UserDTO.user_get
_user_put = UserDTO.user_put


@api.route("/")
@api.expect(_parser)
@api.doc(responses={
    401: "INVALID_TOKEN|EXPIRED_TOKEN|DECODED_USER_NOT_FOUND|TOKEN_IS_MISSING",
    403: "PROFILE_FORBIDDEN_ACCESS",
    404: "USER_NOT_FOUND",
})
class UserResource(Resource):
    @restrict_resource_to_profiles(_INSTITUTE, _EMPLOYEE, _STUDENT)
    @api.marshal_with(_user_get)
    def get(self, user):
        """get self logged"""
        return user, 200

    @restrict_resource_to_profiles(_INSTITUTE, _EMPLOYEE, _STUDENT)
    @api.expect(_user_put, validate=True)
    @api.marshal_with(_user)
    def put(self, user):
        """Change self profile"""
        data = request.json
        return update_user(data, user), 200

    @restrict_resource_to_profiles(_INSTITUTE, _EMPLOYEE, _STUDENT)
    @api.response(204, "User deleted")
    def delete(self, user):
        """Delete self user"""
        return delete_user(user), 204


@api.route("/<int:id>")
class UserByIdResource(Resource):
    @restrict_resource_to_profiles(_INSTITUTE, _EMPLOYEE)
    @api.doc("User deactivate operations", responses={
        204: "User deactivated",
        401: "INVALID_TOKEN|EXPIRED_TOKEN|DECODED_USER_NOT_FOUND|TOKEN_IS_MISSING",
        403: "PROFILE_FORBIDDEN_ACCESS|DEACTIVATE_FORBIDDEN",
        404: "USER_NOT_FOUND",
    })
    @api.expect(_parser)
    def put(self, id: int, user):
        """Deactivate User by id"""
        return deactivate_user(id, user), 204
