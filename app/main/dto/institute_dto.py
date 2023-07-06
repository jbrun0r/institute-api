from flask_restx import Namespace, fields, inputs

from .address_dto import AddressDTO
from .pagination_dto import PaginationDTO
from .user_dto import UserDTO
from .employee_dto import EmployeeDTO


class InstituteDTO:
    api = Namespace("institute", description="Institute related operations")

    institute_filters_parser = api.parser()
    institute_filters_parser.add_argument("trading_name", type=str, location="query")
    institute_filters_parser.add_argument("corporate_name", type=str, location="query")
    institute_filters_parser.add_argument("cnpj",type=inputs.regex(r"(^\d{14}$)"), location="query",)
    institute_filters_parser.add_argument("state", type=str, location="query")
    institute_filters_parser.add_argument("city", type=str, location="query")

    institute_name = api.model(
        "InstituteName",
        {
            "trading_name": fields.String(
                required=True,
                max_length=80,
                description="trading name",
                example="GitHub Inc",
            ),
            "corporate_name": fields.String(
                required=True,
                max_length=80,
                description="corporate name",
                example="GitHub",
            ),
        },
        strict=True
    )

    institute_put = api.clone(
        "InstitutePut",
        institute_name,
        {
            "address": fields.Nested(
                AddressDTO.institute_address,
                required=True,
            ),
        },
    )
    institute_put.__strict__ = True

    institute_post = api.clone(
        "InstitutePost",
        {
            "institute_admin": fields.Nested(
                EmployeeDTO.employee_post,
                required=True,
                skip_none=True,
                attribute=lambda institute: institute.get_admin_employee.user,
            ),
            "cnpj": fields.String(
                required=True,
                description="Institute CNPJ",
                max_length=14,
                pattern=r"(^\d{14}$)",
                example="00000000000000",
            ),
        },
        institute_put,
    )
    institute_post.__strict__ = True

    institute = api.clone("Institute", institute_post)
    institute["institute_admin"].model = EmployeeDTO.employee

    institute_info = api.clone(
        'InstituteInfo',
        institute,
    )

    invite_response = api.clone(
        "InviteResponse",
        EmployeeDTO.employee_role,
        UserDTO.user_post
    )
    invite_response.__strict__ = True

    institutes_paged = api.clone(
        "InstitutesPaged",
        PaginationDTO.pagination_base,
        {
            "items": fields.List(fields.Nested(institute)),
        },
    )
