from json import loads
from flask import request
from flask_restx import Resource

from ..service.document_service import (
    delete_document,
    get_document,
    save_new_document,
    update_document,
    get_all_documents,
)
from ..dto.document_dto import DocumentDTO
from ..dto.auth_dto import AuthenticationDTO
from ..dto.pagination_dto import PaginationDTO
from ..util.auth_utils import restrict_resource_to_profiles, _INSTITUTE, _EMPLOYEE, _STUDENT


api = DocumentDTO.api
_document = DocumentDTO.document
_document_get = DocumentDTO.document_get
_document_paged = DocumentDTO.document_paged
_document_parser = DocumentDTO.document_parser
_document_filters_parser = DocumentDTO.document_filters_parser
_pagination_parser = PaginationDTO.pagination_parser
_parser = AuthenticationDTO.parser


@api.route("/")
@api.doc("Document operations.", responses={
    401: "`INVALID_TOKEN` `EXPIRED_TOKEN` `DECODED_USER_NOT_FOUND` `TOKEN_IS_MISSING`",
    403: "`PROFILE_FORBIDDEN_ACCESS`",
})
class DocumentList(Resource):
    @restrict_resource_to_profiles(_STUDENT)
    @api.response(404, "`USER_NOT_FOUND` `DOCUMENT_NOT_FOUND`")
    @api.marshal_with(_document_get)
    @api.expect(_parser)
    def get(self, user):
        """Get a registered document"""
        return get_document(user), 200

    @restrict_resource_to_profiles(_STUDENT)
    @api.doc("create a new document", responses={
        400: "`INVALID_DOCUMENT` `S3_INTERNAL_ERROR`",
        404: "`USER_NOT_FOUND` `STUDENT_NOT_FOUND`",
        409: "`DOCUMENT_ALREADY_EXISTS`",
    })
    @api.expect(_document_parser)
    @api.marshal_with(_document, code=201, description="Document successfully created")
    def post(self, user):
        """Create a new document"""
        data = request.form.get("json", default={}, type=loads)
        document_file = request.files.get("file", default=None)
        return save_new_document(data, user, document_file), 201

    @restrict_resource_to_profiles(_STUDENT)
    @api.doc(responses={
        400: "`INVALID_DOCUMENT` `S3_INTERNAL_ERROR` `DOCUMENT_UPDATE_FAILED`",
        404: "`USER_NOT_FOUND` `STUDENT_NOT_FOUND` `STUDENT_NOT_FOUND` `FILE_DELETE_FAILED`",
    })
    @api.expect(_document_parser)
    @api.marshal_with(_document, description="Document successfully updated")
    def put(self, user):
        """Update document"""
        data = request.form.get("json", default={}, type=loads)
        document_file = request.files.get("file", default=None)
        return update_document(data, user, document_file), 200

    @restrict_resource_to_profiles(_STUDENT)
    @api.response(404, "`USER_NOT_FOUND` `DOCUMENT_NOT_FOUND` `FILE_DELETE_FAILED`")
    @api.expect(_parser)
    def delete(self, user):
        """Delete document"""
        return delete_document(user), 204


@api.route("/filter/")
class DocumentsListByFilter(Resource):
    @restrict_resource_to_profiles(_INSTITUTE, _EMPLOYEE)
    @api.doc("List of documents by filters", responses={
        401: "`INVALID_TOKEN` `EXPIRED_TOKEN` `DECODED_USER_NOT_FOUND` `TOKEN_IS_MISSING`",
        403: "`PROFILE_FORBIDDEN_ACCESS`",
        404: "`USER_NOT_FOUND` `PAGES_NOT_FOUND`"
    })
    @api.expect(_parser,_pagination_parser, _document_filters_parser, validate=True)
    @api.marshal_list_with(_document_paged)
    def get(self, user):
        """Get registered documents by filters"""
        return get_all_documents(user), 200
