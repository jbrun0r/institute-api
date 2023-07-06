from .. import db
from ..model import User
from ..util.api_error import APIError
from ..service.auth_service import generate_email_validation_token
from ..service.email_service import send_email
from ..service.user_service import save_new_user
from ..service.employee_service import save_employee


def invite_employee(data: dict, user):
    """
    Invite a user to join an institute as an employee.

    Args:
        data (dict): User data for the invitation.
        user: The user sending the invitation.

    Returns:
        dict: The modified user data.
    """
    institute = user.employee.institute
    role = data.pop("role")
    user = save_new_user(data, False, skip_commit=True)
    employee = save_employee(user, institute, role)
    db.session.add(employee)
    db.session.commit()

    send_email(
        email=data["email"],
        template_name="EMPLOYEE_ACTIVATION.html",
        message_subject="Token Employee Activation",
        token_employee_activation=f"{generate_email_validation_token(data['email'])}",
    )
    data["role"] = role
    return data


def invite_student(data: dict, user):
    """
    Invite a user to join an institute as an employee.

    Args:
        data (dict): User data for the invitation.
        user: The user sending the invitation.

    Raises:
        APIError: If the user already exists and is active or if the user already exists.

    Returns:
        dict: The modified user data.
    """

    if User.query.filter_by(email=data["email"]).first():
        if user.activation_status:
            raise APIError("User already exists and is active.", code=409, api_code="USER_ALREADY_ACTIVE")
        else:
            raise APIError("User already exists.", code=409, api_code="USER_ALREADY_EXISTS")

    send_email(
        email=data["email"],
        template_name="STUDENT_VALIDATION.html",
        message_subject="Token Student Validation",
        token_student_validation=generate_email_validation_token([data["email"], user.email]),
    )

    return data
