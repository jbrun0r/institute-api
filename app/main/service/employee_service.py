from .. import db
from ..util.api_error import APIError
from ..model import Employee, User
from ..util.pagination_utils import paginate, get_user_filters
from ..service.user_service import delete_user
from sqlalchemy.sql import text


def save_employee(user: User, institute, role=None) -> Employee:
    """
    Save a new employee.

    Args:
        user (User): User object representing the employee.
        institute: Institute associated with the employee.
        role: Role of the employee (optional).

    Returns:
        Employee: The created employee object.
    """
    employee = Employee(
        user=user,
        institute=institute,
        role=role
    )
    db.session.add(employee)
    db.session.commit()
    return employee


def update_employee(user: User, data, id) -> User:
    """
    Update employee details.

    Args:
        user (User): User object representing the current user.
        data (dict): Data containing the updated attributes.
        id: ID of the employee to be updated.

    Returns:
        User: The updated user object.
    """
    employee = next((emp for emp in user.employee.institute.employees if emp.user_id == id), None)
    if employee:
        for attribute, new_value in data.items():
            setattr(employee.user, attribute, new_value)
        db.session.commit()
        return employee.user
    raise APIError("Employee doesn't exist.", code=404, api_code="EMPLOYEE_NOT_FOUND")


def get_employees(user: User):
    """
    Get a paginated list of employees associated with the user's institute.

    Args:
        user (User): User object representing the current user.

    Returns:
        Pagination: Paginated list of User objects representing the employees.
    """
    user_filter = get_user_filters() 
    user_filter.append(text(f"employees.institute_id = {user.employee.institute_id}"))
    return paginate(User, Employee, filter=user_filter)


def delete_employee(user: User, id):
    """
    Delete an employee.

    Args:
        user (User): User object representing the current user.
        id: ID of the employee to be deleted.
    """
    employee = next((emp for emp in user.employee.institute.employees if emp.user_id == id and emp.user_id != user.id), None)
    if employee:
        delete_user(employee.user)
        return
    raise APIError("Employee doesn't exist.", code=404, api_code="EMPLOYEE_NOT_FOUND")
