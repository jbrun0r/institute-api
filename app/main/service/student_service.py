from .. import db
from ..util.api_error import APIError
from ..model import User, Address, Student, Institute
from ..service.user_service import save_new_user, update_user
from ..service.auth_service import decode_email_validation_token
from ..util.pagination_utils import paginate, get_student_filters
from ..util.auth_utils import _STUDENT, _INSTITUTE

from datetime import datetime


def save_new_student(data: dict, token: str) -> Student:
    """
    Save a new student.

    Args:
        data (dict): Student data.
        token (str): Token for email validation.

    Returns:
        Student: The newly created student.
    """
    student_email, institute_email = decode_email_validation_token(token)

    address_data = data.pop("address")
    user_data = data.pop("user")
    user_data["email"] = student_email

    institute_user = User.query.filter_by(email=institute_email, profile=_INSTITUTE).first()
    if not institute_user:
        raise APIError("Institute user not found or invalid profile.", code=404, api_code="INSTITUTE_USER_NOT_FOUND")

    if User.query.filter_by(email=student_email).first():
        raise APIError("User already exists.", code=409, api_code="USER_ALREADY_EXISTS")

    data["birthday_date"] = datetime.strptime(data["birthday_date"], r"%Y-%m-%d")
    
    user_data["profile"] = _STUDENT
    user = save_new_user(user_data)
    new_student = Student(
        **data,
        user=user,
        address=Address(**address_data),
        institute=institute_user.employee.institute,
    )

    save(new_student)
    return new_student


def save(data: Student) -> None:
    """
    Save a student to the database.

    Args:
        data (Student): The student object to save.
    """
    db.session.add(data)
    db.session.commit()


def update_student(data: dict, user: User) -> Student:
    """
    Update a student's information.

    Args:
        data (dict): Updated student data.
        user (User): The user associated with the student.

    Returns:
        Student: The updated student.
    """
    student = user.student
    user_data = data.pop("user")
    update_user(user_data, user)

    address_data = data.pop("address")
    for field_name, value in address_data.items():
        setattr(student.address, field_name, value)

    student.gender = data["gender"]
    student.disabled_person = data["disabled_person"]
    student.birthday_date = datetime.strptime(data["birthday_date"], r"%Y-%m-%d")
    db.session.commit()
    return student


def delete(user: User) -> None:
    """
    Delete a student from the database.

    Args:
        user (User): The user associated with the student.
    """
    db.session.delete(user.student)
    db.session.commit()


def get_all_students() -> paginate:
    """
    Get all students.

    Returns:
        paginate: Paginated results of students.
    """
    students_filter = get_student_filters()
    return paginate(table=Student, filter=students_filter)


def find_student_by_id(id: int, user: User) -> Student:
    """
    Find a student by ID.

    Args:
        id (int): The ID of the student to find.
        user (User): The user making the request.

    Returns:
        Student: The found student.

    Raises:
        APIError: If the student is not found or the user does not have access.
    """
    if user.profile.value == "student" and user.student.id != id:
        raise APIError("Student cannot access another student's data.", code=403, api_code="STUDENT_FORBIDDEN_ACCESS")

    student = Student.query.filter_by(id=id).first()
    if not student:
        raise APIError(
            "Student ID does not exist. Please use an existing ID.",
            code=404,
            api_code="STUDENT_NOT_FOUND",
        )

    return student
