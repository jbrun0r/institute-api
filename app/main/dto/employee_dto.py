from flask_restx import Namespace, fields

from app.main.dto.user_dto import UserDTO


class EmployeeDTO:
    api = Namespace("employee", description="Employee related operations")

    employee_role = api.model(
        "EmployeeRole",
        {
            "role": fields.String(
                required=True,
                description="role",
                max_length=80,
                example="CEO",
            ),
        },
    )

    employee_post = api.clone(
        "EmployeePost",
        UserDTO.user_post,
        employee_role,
    )
    employee_post.__strict__ = True

    employee = api.clone(
        "EmployeeUser",
        UserDTO.user,
        employee_role,
    )
    employee.__strict__ = True
