from flask_restx import Resource

from ..dto.error_dto import ErrorsDTO
from ..dto.pagination_dto import PaginationDTO
from ..service.error_service import get_filtered_errors

api = ErrorsDTO.api
_error = ErrorsDTO.error
_error_response = ErrorsDTO.error_response
_error_paged = ErrorsDTO.error_paged
_error_filters_parser = ErrorsDTO.error_filters_parser
_pagination_parser = PaginationDTO.pagination_parser


@api.route("/")
class ErrorResource(Resource):
    @api.doc(responses={
        200: "Success",
        404: "`PAGES_NOT_FOUND`"
    })
    @api.expect(_pagination_parser, _error_filters_parser, validate=True)
    @api.marshal_list_with(_error_paged, code=200, description="List of errors")
    def get(self):
        """Get a list of errors."""
        return get_filtered_errors(), 200
