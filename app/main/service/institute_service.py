from .. import db
from ..util.api_error import APIError
from ..model import User, Address, Institute
from ..util.pagination_utils import paginate, get_institute_filters
from ..service.user_service import save_new_user
from ..service.email_service import send_email
from ..service.employee_service import save_employee
from ..service.auth_service import generate_email_validation_token
from ..util.auth_utils import _INSTITUTE
from pycpfcnpj.cpfcnpj import validate


def save_new_institute(data):
    """
    Save a new institute.

    Args:
        data (dict): Data for the new institute.

    Returns:
        Institute: The newly created institute.
    Raises:
        APIError: If the provided CNPJ is not valid, if the institute already exists, or if the email already exists.
    """
    if not validate(data["cnpj"]):
        raise APIError("The CNPJ provided is not valid.", code=406, api_code="INVALID_CNPJ")
    
    if User.query.filter_by(email=data["institute_admin"]["email"]).first():
        raise APIError("User already exists", code=409, api_code="USER_ALREADY_EXISTS")

    if Institute.query.filter_by(cnpj=data["cnpj"]).first():
        raise APIError("Institute already exists.", code=409, api_code="INSTITUTE_ALREADY_EXISTS")

    user_dict = data.pop("institute_admin")
    role = user_dict.pop("role")

    address_dict = data.pop("address")
    user_dict["profile"] = _INSTITUTE
    institute = Institute(
        **data,
        address=Address(**address_dict),
    )
    new_user = save_new_user(user_dict, skip_commit=True)
    employee = save_employee(new_user, institute, role)
    db.session.add(employee)
    db.session.commit()
    return institute


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


def update_institute(data: dict, user: User) -> Institute:
    """
    Update an existing institute.

    Args:
        data (dict): Updated data for the institute.
        user (User): User performing the update.

    Returns:
        Institute: The updated institute.
    Raises:
        APIError: If the institute does not exist.
    """
    if institute := user.employee.institute:
        for key, value in data.pop("address", {}).items():
            setattr(institute.address, key, value)
        for key, value in data.items():
            setattr(institute, key, value)

        db.session.commit()
        return institute
    raise APIError("Institute doesn't exists.", code=404, api_code="INSTITUTE_NOT_FOUND")


def delete_institute(user: User):
    """
    Delete an institute.

    Args:
        user (User): User requesting the deletion.
    """
    db.session.delete(user.employee.institute)
    db.session.commit()


def get_all_institutes():
    """
    Get a paginated list of all institutes.

    Returns:
        Pagination: Paginated list of Institute objects.
    """
    institutes_filter = get_institute_filters()
    return paginate(Institute, Address, filter=institutes_filter)


def find_institute_by(**institute_attr) -> Institute:
    """
    Find an institute by the provided attributes.

    Args:
        **institute_attr: Attributes to filter the institute by.

    Returns:
        Institute: The found institute.
    Raises:
        APIError: If the institute is not found.
    """
    if institute := Institute.query.filter_by(**institute_attr).first():
        return institute
    raise APIError(f"Institute not found by params {institute_attr}", code=404, api_code="INSTITUTE_QUERY_NOT_FOUND")


def institute_info(user: User):
    """
    Get the information of an institute.

    Args:
        user (User): User associated with the institute.

    Returns:
        Institute: The institute information.
    """
    return user.employee.institute
