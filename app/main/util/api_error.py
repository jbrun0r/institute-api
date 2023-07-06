from .. import db
from ..model import Error
from werkzeug.exceptions import HTTPException


class APIError(HTTPException):
    """
    Custom exception class representing a default or generic error.

    Attributes:
        message (str): Error message (default: "Generic error").
        info (dict): Additional information about the error (default: None).
        code (int): HTTP status code for the error (default: None).
        api_code (str): API-specific error code (default: None).
    """

    def __init__(self, message="Generic error", info=None, code=None, api_code=None):
        """
        Initialize the APIError instance.

        Args:
            message (str, optional): Error message (default: "Generic error").
            info (dict, optional): Additional information about the error (default: None).
            code (int, optional): HTTP status code for the error (default: None).
            api_code (str, optional): API-specific error code (default: None).
        """
        self.code = code
        self.description = message
        self.info = info
        self.api_code = (api_code or message).upper().replace(' ', '_').replace('.', '')

        super().__init__()

    def to_error(self) -> Error:
        """
        Convert the APIError to an Error model instance.

        If an Error instance with the same api_code already exists in the database, update its description.
        Otherwise, create a new Error instance and add it to the database.

        Returns:
            Error: The converted Error model instance.
        """
        if error := Error.query.filter_by(api_code=self.api_code).first():
            error.description = self.description
        else:
            error = Error(
                code=self.code,
                api_code=self.api_code,
                name=self.name,
                description=self.description,
            )
            db.session.add(error)
            db.session.commit()

        if self.info:
            error.info = self.info

        return error
    
    @classmethod
    def add_errors_to_database(cls):
        """
        Add API errors to the database.

        Iterate over the API_ERROR_CODES dictionary and add each error to the database as an Error instance.
        """

        for api_code, api_error in API_ERROR_CODES.items():
            db.session.add(Error(api_code=api_code, **api_error))
        db.session.commit()


API_ERROR_CODES = {
    "FAILED_DECODE": {
        "code": 400,
        "name": "Bad Request",
        "description": "Invalid token to decode. Maybe expired",
    },
    "S3_INTERNAL_ERROR": {
        "code": 400,
        "name": "Bad Request",
        "description": "Upload error",
    },
    "S3_FAILED_URL_GENERATE": {
        "code": 400,
        "name": "Bad Request",
        "description": "Internal error on generate presigned URL for download.",
    },
    "USER_NOT_ACTIVATED": {
        "code": 400,
        "name": "Bad Request",
        "description": "User's account isn't active yet",
    },
    "WRONG_CONFIRM_PASSWORD": {
        "code": 400,
        "name": "Bad Request",
        "description": "Password doesn't match",
    },
    "DOCUMENT_UPDATE_FAILED": {
        "code": 400,
        "name": "Bad Request",
        "description": "Document update failed.",
    },
    "INVALID_DATA": {
        "code": 400,
        "name": "Bad Request",
        "description": "Invalid Data.",
    },
    "FAILED_LOGIN": {
        "code": 401,
        "name": "Unauthorized",
        "description": "Incorrect User or Password",
    },
    "EXPIRED_TOKEN": {
        "code": 401,
        "name": "Unauthorized",
        "description": "Expired login token",
    },
    "INVALID_TOKEN": {
        "code": 401,
        "name": "Unauthorized",
        "description": "Invalid login Token",
    },
    "TOKEN_IS_MISSING": {
        "code": 401,
        "name": "Unauthorized",
        "description": "Token is missing.",
    },
    "WRONG_PASSWORD": {
        "code": 401,
        "name": "Unauthorized",
        "description": "Invalid password",
    },
    "USER_ALREADY_ACCESSED": {
        "code": 403,
        "name": "Forbidden",
        "description": "User has already logged in for the first time",
    },
    "STUDENT_FORBIDDEN_ACCESS": {
        "code": 403,
        "name": "Forbidden",
        "description": "Student cannot access another student's data",
    },
    "DEACTIVATE_FORBIDDEN": {
        "code": 403,
        "name": "Forbidden",
        "description": "Can't deactivate user.",
    },
    "PROFILE_FORBIDDEN_ACCESS": {
        "code": 403,
        "name": "Forbidden",
        "description": "User cannot access",
    },
    "ADDRESS_NOT_FOUND": {
        "code": 404,
        "name": "Not Found",
        "description": "Address doesn't exist.",
    },
    "STUDENT_NOT_FOUND": {
        "code": 404,
        "name": "Not Found",
        "description": "Student ID doesn't exist. Please use an existing ID.",
    },
    "INSTITUTE_NOT_FOUND": {
        "code": 404,
        "name": "Not Found",
        "description": "Institute doesn't exist.",
    },
    "INSTITUTE_QUERY_NOT_FOUND": {
        "code": 404,
        "name": "Not Found",
        "description": "Institute not found by params",
    },
    "DECODED_USER_NOT_FOUND": {
        "code": 404,
        "name": "Not Found",
        "description": "Decoded token does not refer to a user",
    },
    "EMAIL_NOT_FOUND": {
        "code": 404,
        "name": "Not Found",
        "description": "User with this email doesn't exist!",
    },
    "FILE_NOT_FOUND": {
        "code": 404,
        "name": "Not Found",
        "description": "Uploaded file not found",
    },
    "FILE_DELETE_FAILED": {
        "code": 404,
        "name": "Not Found",
        "description": "Unable to delete uploaded file as it was not found",
    },
    "PAGES_NOT_FOUND": {
        "code": 404,
        "name": "Not Found",
        "description": "No page generated",
    },
    "DOCUMENT_NOT_FOUND": {
        "code": 404,
        "name": "Not Found",
        "description": "Document doesn't exist.",
    },
    "USER_NOT_FOUND": {
        "code": 404,
        "name": "Not Found",
        "description": "User doesn't exist.",
    },
    "PAGE_NOT_FOUND": {
        "code": 404,
        "name": "Not Found",
        "description": "Page doesn't exist.",
    },
    "EMPLOYEE_NOT_FOUND": {
        "code": 404,
        "name": "Not Found",
        "description": "Employee doesn't exist.",
    },
    "FILE_NOT_INDEXED": {
        "code": 406,
        "name": "Not Acceptable",
        "description": "No files indexed to upload",
    },
    "INVALID_CNPJ": {
        "code": 406,
        "name": "Not Acceptable",
        "description": "The CNPJ provided is not valid",
    },
    "DOCUMENT_ALREADY_EXISTS": {
        "code": 409,
        "name": "Conflict",
        "description": "DOCUMENT already exists",
    },
    "INSTITUTE_ALREADY_EXISTS": {
        "code": 409,
        "name": "Conflict",
        "description": "Institute already exists.",
    },
    "STUDENT_ALREADY_EXISTS": {
        "code": 409,
        "name": "Conflict",
        "description": "Student already exists",
    },
    "USER_ALREADY_EXISTS": {
        "code": 409,
        "name": "Conflict",
        "description": "User already exists",
    },
    "USER_IS_ACTIVE": {
        "code": 409,
        "name": "Conflict",
        "description": "User is already active",
    },
    "USER_ALREADY_ACTIVE": {
        "code": 409,
        "name": "Conflict",
        "description": "User already exists and is active.",
    },
    "UNSUPPORTED_FILE": {
        "code": 415,
        "name": "Unsupported Media Type",
        "description": "Unsupported file format",
    },
    "WRONG_NEW_PASSWORD": {
        "code": 422,
        "name": "Unprocessable Entity",
        "description": "New password cannot be the same as the current one",
    },
}
