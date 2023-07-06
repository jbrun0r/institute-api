from flask import request
from flask_restx import Resource

from ..dto.pagination_dto import PaginationDTO
from ..dto.user_dto import UserDTO
from ..dto.employee_dto import EmployeeDTO
from ..dto.auth_dto import AuthenticationDTO
from ..service.employee_service import update_employee, get_employees, delete_employee
from ..util.auth_utils import restrict_resource_to_profiles, _INSTITUTE


api = EmployeeDTO.api
_parser = AuthenticationDTO.parser
_pagination_parser = PaginationDTO.pagination_parser
_user_put = UserDTO.user_put
_user_paged = UserDTO.user_paged
_user_filters_parser = UserDTO.user_filters_parser


@api.route("/<int:id>")
@api.doc("Employee update operations", responses={
    401: "`INVALID_TOKEN` `EXPIRED_TOKEN` `DECODED_USER_NOT_FOUND` `TOKEN_IS_MISSING`",
    403: "`PROFILE_FORBIDDEN_ACCESS`",
    404: "`USER_NOT_FOUND`",
})
class EmployeeByIdResource(Resource):
    @restrict_resource_to_profiles(_INSTITUTE)
    @api.response(200, description="User updated")
    @api.expect(_parser, _user_put, validate=True)
    @api.marshal_with(_user_put)
    def put(self, id, user):
        """Update employee by ID"""
        data = request.json
        return update_employee(user, data, id), 200

    @restrict_resource_to_profiles(_INSTITUTE)
    @api.response(204, description="Deleted user")
    @api.expect(_parser)
    def delete(self, id, user):
        """Delete employee by ID"""
        return delete_employee(user, id), 204


@api.route("/")
class EmployeeListResource(Resource):
    @restrict_resource_to_profiles(_INSTITUTE)
    @api.doc("Employee list operations", responses={
        200: "Employee list",
        401: "`INVALID_TOKEN` `EXPIRED_TOKEN` `DECODED_USER_NOT_FOUND` `TOKEN_IS_MISSING`",
        403: "`PROFILE_FORBIDDEN_ACCESS`",
        404: "`USER_NOT_FOUND` `PAGE_NOT_FOUND`",
    })
    @api.expect(_parser, _pagination_parser, _user_filters_parser, validate=True)
    @api.marshal_with(_user_paged)
    def get(self, user):
        """Get employee list"""
        return get_employees(user), 200
