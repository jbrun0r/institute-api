from flask_restx import Namespace, fields, inputs

from ..model.student import Gender
from .address_dto import AddressDTO
from .user_dto import UserDTO
from .pagination_dto import PaginationDTO


class StudentDTO:
    api = Namespace("student", description="Student related operations")

    student_filters_parser = api.parser()
    student_filters_parser.add_argument("name", type=str, location="query")
    student_filters_parser.add_argument("date_lower",type=inputs.regex(r"([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))"),location="query")
    student_filters_parser.add_argument("date_upper",type=inputs.regex(r"([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))"),location="query")
    student_filters_parser.add_argument("state", type=str, location="query")
    student_filters_parser.add_argument("city", type=str, location="query")
    student_filters_parser.add_argument("gender",type=str,location="query",choices=Gender._member_names_)

    student_id = api.parser().add_argument("student_id", type=int, location="query")

    student_put = api.model(
        "StudentPut",
        {
            "gender": fields.String(
                required=True,
                description="Student gender",
                enum=Gender._member_names_,
            ),
            "disabled_person": fields.Boolean(
                required=True,
                default=False,
                description="Student identifies as a person with a disability",
            ),
            "birthday_date": fields.Date(
                required=True,
                description="Students birthday date",
            ),
            "user": fields.Nested(
                UserDTO.user_put,
                required=True,
            ),
            "address": fields.Nested(
                AddressDTO.address,
                required=True,
            ),
        },
        strict=True,
    )

    user_student = api.clone(
        "UserStudent",
        UserDTO.user_put,
        {
            "phone_number": fields.String(
                required=True,
                description="Student phone number. doesn't accept empty string",
                max_length=11,
                example="85999999999",
                pattern=r"^$|^[1-9]{2}(?:[2-8]|9[1-9])[0-9]{3}[0-9]{4}$",
            ),
        }
    )

    student_post = api.clone(
        "StudentPost",
        student_put,
        {
            "user": fields.Nested(
                user_student,
                required=True,
            ),
        },
    )
    student_post.__strict__ = True

    student = api.clone(
        "Student",
        {
            "id": fields.Integer(description="Students id"),
            "document_id": fields.Integer(
                description="Students document id",
                attribute=lambda student: student.document and student.document.id,
            ),
        },
        student_post,
        {
            "user": fields.Nested(
                UserDTO.user,
                required=True,
            ),
        },
    )

    student_paged = api.clone(
        "StudentPaged",
        PaginationDTO.pagination_base,
        {
            "items": fields.List(fields.Nested(student)),
        },
    )
