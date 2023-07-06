from flask_restx import Namespace, fields, inputs, reqparse

from .pagination_dto import PaginationDTO


class ErrorsDTO:
    api = Namespace("error", description="API erors operations")

    error_filters_parser = reqparse.RequestParser()
    error_filters_parser.add_argument("code", type=inputs.regex(r"^[1-5][0-9]{2}$"), location="query")
    error_filters_parser.add_argument("api_code", type=str, location="query")
    error_filters_parser.add_argument("description", type=str, location="query")

    error = api.model(
        "Error",
        {
            "code": fields.Integer(
                required=True,
                description="HTTP status code",
                min=400,
                max=599,
            ),
            "name": fields.String(
                required=True,
                description="HTTP status name",
            ),
            "api_code": fields.String(
                required=True,
                description="API error code",
            ),
            "description": fields.String(
                required=True,
                description="Error description",
            ),
            "info": fields.String(
                required=False,
                description="Specific error details",
                default=None,
            ),
        },
    )

    error_response = api.model(
        "ErrorResponse",
        {
            "error": fields.Nested(error, skip_none=True),
        },
    )

    error_paged = api.clone(
        "ErrorPaged",
        PaginationDTO.pagination_base,
        {
            "items": fields.List(fields.Nested(error, skip_none=True)),
        },
    )
