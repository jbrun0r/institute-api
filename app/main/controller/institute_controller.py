from flask import request
from flask_restx import Resource

from ..service.institute_service import (delete_institute, get_all_institutes,
                                         save_new_institute, update_institute,
                                         institute_info, invite_employee,
                                         invite_student,
                                       )
from ..dto.address_dto import AddressDTO
from ..dto.institute_dto import InstituteDTO, UserDTO
from ..dto.auth_dto import AuthenticationDTO
from ..dto.pagination_dto import PaginationDTO
from ..util.auth_utils import require_token, restrict_resource_to_profiles, _INSTITUTE, _EMPLOYEE


address_ns = AddressDTO.api
api = InstituteDTO.api
_parser = AuthenticationDTO.parser
_student_email = UserDTO.user_email
_institute_post = InstituteDTO.institute_post
_institute = InstituteDTO.institute
_institute_info = InstituteDTO.institute_info
_institute_put = InstituteDTO.institute_put
_institute_filters_parser = InstituteDTO.institute_filters_parser
_institutes_paged = InstituteDTO.institutes_paged
_invite_response = InstituteDTO.invite_response
_pagination_parser = PaginationDTO.pagination_parser


@api.route("/")
class InstituteList(Resource):
    @require_token
    @api.doc(responses={
        200: "Success",
        401: "`INVALID_TOKEN` `EXPIRED_TOKEN` `TOKEN_IS_MISSING`",
        404: "`USER_NOT_FOUND` `PAGES_NOT_FOUND`"
    })
    @api.expect(_parser, _pagination_parser, _institute_filters_parser, validate=True)
    @api.marshal_list_with(_institutes_paged, code=200, description="List of registered institutes")
    def get(self):
        """List all registered institutes."""
        return get_all_institutes(), 200

    @api.expect(_institute_post, validate=True)
    @api.doc(responses={
        201: "Institute successfully created",
        406: "`INVALID_CNPJ` `INVALID_STATE_REGISTRATION`",
        409: "`USER_ALREADY_EXISTS` `INSTITUTE_ALREADY_EXISTS`"
    })
    @api.marshal_with(_institute, code=201, description="Institute successfully created")
    def post(self):
        """Create a new institute."""
        data = request.json
        return save_new_institute(data=data), 201


    @restrict_resource_to_profiles(_INSTITUTE)
    @api.expect(_parser, _institute_put, validate=True)
    @api.doc(responses={
        200: "Institute successfully updated",
        401: "`INVALID_TOKEN` `EXPIRED_TOKEN` `DECODED_USER_NOT_FOUND` `TOKEN_IS_MISSING`",
        403: "`PROFILE_FORBIDDEN_ACCESS`",
        404: "`USER_NOT_FOUND` `INSTITUTE_NOT_FOUND`"
    })
    @api.marshal_with(_institute, description="Institute successfully updated")
    def put(self, user):
        """Update institute."""
        data = request.json
        return update_institute(data, user), 200


    @restrict_resource_to_profiles(_INSTITUTE)
    @api.response(204, "Institute deleted")
    @api.doc(responses={
        204: "Institute deleted",
        401: "`INVALID_TOKEN` `EXPIRED_TOKEN` `DECODED_USER_NOT_FOUND` `TOKEN_IS_MISSING`",
        403: "`PROFILE_FORBIDDEN_ACCESS`",
        404: "`USER_NOT_FOUND`"
    })
    @api.expect(_parser)
    def delete(self, user):
        """Delete institute."""
        return delete_institute(user), 204


@api.route("/invite/employee/")
@api.doc(responses={
    401: "`INVALID_TOKEN` `EXPIRED_TOKEN` `DECODED_USER_NOT_FOUND` `TOKEN_IS_MISSING`",
    403: "`PROFILE_FORBIDDEN_ACCESS`",
    404: "`USER_NOT_FOUND`",
    409: "`USER_ALREADY_EXISTS` `EMPLOYEE_ALREADY_EXISTS` `EMPLOYEE_ALREADY_ACTIVE`",
})
class InviteEmployee(Resource):
    @restrict_resource_to_profiles(_INSTITUTE)
    @api.expect(_invite_response, _parser, validate=True)
    @api.marshal_list_with(_invite_response, description="Email sent to destination")
    def post(self, user):
        """Invite a new employee to the institute."""
        data = request.json
        return invite_employee(data, user)


@api.route("/invite/student/")
@api.doc(responses={
    401: "`INVALID_TOKEN` `EXPIRED_TOKEN` `DECODED_USER_NOT_FOUND` `TOKEN_IS_MISSING`",
    403: "`PROFILE_FORBIDDEN_ACCESS`",
    404: "`USER_NOT_FOUND`",
    409: "`USER_ALREADY_EXISTS` `EMPLOYEE_ALREADY_EXISTS` `EMPLOYEE_ALREADY_ACTIVE`",
})
class InviteStudent(Resource):
    @restrict_resource_to_profiles(_INSTITUTE)
    @api.expect(_student_email, _parser, validate=True)
    @api.marshal_with(_student_email, description="Email sent to destination")
    def post(self, user):
        """Invite a new student to the institute."""
        data = request.json
        return invite_student(data, user)

@api.route("")
class InstituteInformationResource(Resource):
    @restrict_resource_to_profiles(_INSTITUTE, _EMPLOYEE)
    @api.doc(responses={
        401: "`INVALID_TOKEN` `EXPIRED_TOKEN` `DECODED_USER_NOT_FOUND` `TOKEN_IS_MISSING`",
        403: "`PROFILE_FORBIDDEN_ACCESS`",
        404: "`USER_NOT_FOUND`",
    })
    @api.marshal_with(_institute_info)
    @api.expect(_parser)
    def get(self, user):
        """Get institute information."""
        return institute_info(user), 200
