from flask import request
from flask_restx import Resource

from ..service.student_service import (delete, find_student_by_id,
                                         get_all_students,
                                         save_new_student, update_student)
from ..dto.student_dto import StudentDTO
from ..dto.auth_dto import AuthenticationDTO
from ..dto.pagination_dto import PaginationDTO
from ..util.auth_utils import restrict_resource_to_profiles, _INSTITUTE, _EMPLOYEE, _STUDENT

api = StudentDTO.api
_student = StudentDTO.student
_student_post = StudentDTO.student_post
_student_put = StudentDTO.student_put
_student_paged = StudentDTO.student_paged
_student_filters_parser = StudentDTO.student_filters_parser
_pagination_parser = PaginationDTO.pagination_parser
_parser = AuthenticationDTO.parser


@api.route("/<string:token>")
class StudentCreate(Resource):
    @api.expect(_student_post, validate=True)
    @api.response(409, "USER_ALREADY_EXISTS")
    @api.marshal_with(_student, code=201, description="Student successfully created")
    def post(self, token):
        """Create a new student"""
        data = request.json
        return save_new_student(data=data, token=token), 201

@api.route("/")
class StudentList(Resource):
    @restrict_resource_to_profiles(_INSTITUTE, _EMPLOYEE, get_user=False)
    @api.doc(responses={
        401: "INVALID_TOKEN|EXPIRED_TOKEN|DECODED_USER_NOT_FOUND|TOKEN_IS_MISSING",
        403: "PROFILE_FORBIDDEN_ACCESS",
        404: "USER_NOT_FOUND|PAGES_NOT_FOUND"
    })
    @api.expect(_parser, _pagination_parser, _student_filters_parser, validate=True)
    @api.marshal_list_with(_student_paged)
    def get(self):
        """List all registered students"""
        return get_all_students(), 200


    @restrict_resource_to_profiles(_STUDENT)
    @api.doc(responses={
        401: "INVALID_TOKEN|EXPIRED_TOKEN|DECODED_USER_NOT_FOUND|TOKEN_IS_MISSING",
        403: "PROFILE_FORBIDDEN_ACCESS",
        404: "USER_NOT_FOUND"
    })
    @api.expect(_student_put, _parser, validate=True)
    @api.marshal_with(_student_put, description="Student successfully updated")
    def put(self, user):
        """Update student"""
        data = request.json
        return update_student(data, user), 200


    @restrict_resource_to_profiles(_STUDENT)
    @api.doc("delete student", responses={
        204: "Student successfully deleted",
        401: "INVALID_TOKEN|EXPIRED_TOKEN|DECODED_USER_NOT_FOUND|TOKEN_IS_MISSING",
        403: "PROFILE_FORBIDDEN_ACCESS",
        404: "USER_NOT_FOUND"
    })
    @api.expect(_parser)
    def delete(self, user):
        """Delete student"""
        return delete(user), 204


@api.route("/<int:id>")
class StudentListWithID(Resource):
    @restrict_resource_to_profiles(_INSTITUTE, _EMPLOYEE, _STUDENT)
    @api.doc("registered student by id", responses={
        401: "INVALID_TOKEN|EXPIRED_TOKEN|DECODED_USER_NOT_FOUND|TOKEN_IS_MISSING",
        403: "STUDENT_FORBIDDEN_ACCESS",
        404: "USER_NOT_FOUND|STUDENT_NOT_FOUND"
    })
    @api.expect(_parser)
    @api.marshal_list_with(_student)
    def get(self, id, user):
        """Get a registered student"""
        return find_student_by_id(id, user), 200
