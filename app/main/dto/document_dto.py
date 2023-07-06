from flask_restx import Namespace, fields
from werkzeug.datastructures import FileStorage

from ..util.document_validation_utils import parse_request_value
from .auth_dto import AuthenticationDTO
from .pagination_dto import PaginationDTO


class DocumentDTO:
    api = Namespace("document", description="Document related operations")

    document_filters_parser = api.parser().add_argument("title", type=str, location="query")

    document_fields = api.model("DocumentFields", {
        "title": fields.String(
            max_length=100,
            required=True,
            description="Document title",
            example="School Record"
        ),
        "key": fields.String(
            max_length=100,
            description="Uniquely identifies the object in an Amazon S3 bucket",
            example="student_id.pdf"
        )
    })

    document = api.model("Document", {
        **document_fields,
    })

    document_get = api.model("DocumentGet", {
        **document_fields,
    })

    document_parser = AuthenticationDTO.parser.copy().add_argument(
        "file",
        location='files',
        type=FileStorage
    )
    document_parser.add_argument(
        "json",
        required=True,
        location="form",
        type=parse_request_value,
    )

    document_paged = api.model("DocumentPaged", {
        **PaginationDTO.pagination_base,
        "items": fields.List(fields.Nested(document)),
    })
