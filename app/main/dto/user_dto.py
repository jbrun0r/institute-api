from flask_restx import Namespace, fields

from ..model.user import Profile
from .address_dto import AddressDTO
from .pagination_dto import PaginationDTO


email_pattern = r"^(?:[\w]+|([-_.])(?!\1))+@+(?:[\w]+|([-_.])(?!\1))(\.[\w]{2,10})+$"
phone_number_pattern = r"^$|^[1-9]{2}(?:[2-8]|9[1-9])[0-9]{3}[0-9]{4}$"


class UserDTO:
    api = Namespace("user", description="User related operations")

    user_filters_parser = api.parser()
    user_filters_parser.add_argument("search", type=str, location="query")
    user_filters_parser.add_argument("profile",type=str,choices=[profile for profile in Profile._member_names_ if profile != "student"])

    user_put = api.model(
        "UserPut",
        {
            "name": fields.String(
                required=True,
                description="User's full name",
                max_length=80,
                example="João Bruno Rodrigues"
            ),
            "phone_number": fields.String(
                required=True,
                description="User phone number",
                max_length=11,
                example="85999999999",
                pattern=phone_number_pattern,
            ),
        },
        strict=True,
    )

    user_email = api.model(
        "UserEmail",
        {
            "email": fields.String(
                required=True,
                description="User's email",
                example="jbrun0r@github.com",
                max_length=128,
                pattern=email_pattern,
            ),
        },
        strict=True,
    )
    user_post = api.clone(
        "UserPost",
        user_put,
        user_email,
    )
    user_post.__strict__ = True

    user = api.clone(
        "User",
        {
            "id": fields.Integer(required=False),
            "profile": fields.String(
                enum=Profile._member_names_,
                default="employee",
                description="User's profile",
            ),
            "activation_status": fields.Boolean(description="User status."),
        },
        user_post,
    )

    user_get = api.clone(
        "UserGet",
        user,
        {
            "address": fields.Nested(
                AddressDTO.address,
                allow_null=True,
                attribute=lambda user: user.student and user.student.address,
                description="If profile is 'student', show student address, null otherwise",
            ),
        },
    )

    user_auth = api.inherit(
        "UserAuth",
        user,
    )

    user_paged = api.clone(
        "UserPaged",
        PaginationDTO.pagination_base,
        {
            "items": fields.List(fields.Nested(user)),
        },
    )
