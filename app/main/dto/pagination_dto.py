from flask_restx import Namespace, fields, reqparse


class PaginationDTO:
    api = Namespace(
        "pagination",
        required=True,
        description="Pagination related operations",
    )

    pagination_base = api.model(
        "PaginationBase",
        {
            "total": fields.Integer(required=True, description="Total"),
            "limit": fields.Integer(required=True, description="Limit"),
            "page": fields.Integer(required=True, description="Page"),
            "pages": fields.Integer(required=True, description="Pages"),
            "per_page": fields.Integer(required=True, description="Per Page"),
            "prev_num": fields.Integer(required=True, description="Prev Num"),
            "next_num": fields.Integer(required=True, description="Next Num"),
        },
    )

    pagination_parser = reqparse.RequestParser()
    pagination_parser.add_argument("page", type=int, location="query")
    pagination_parser.add_argument("per_page", type=int, location="query")

    page_parser = reqparse.RequestParser()
    page_parser.add_argument("page", type=int, location="query")

    per_page_parser = reqparse.RequestParser()
    per_page_parser.add_argument("per_page", type=int, location="query")
