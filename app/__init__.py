from flask import Blueprint
from flask_restx import Api

from .main.controller.auth_controller import api as auth_ns
from .main.controller.document_controller import api as document_ns
from .main.controller.employee_controller import api as employee_ns
from .main.controller.error_controller import _error_response, api as error_ns
from .main.controller.institute_controller import api as institute_ns, address_ns
from .main.controller.student_controller import api as student_ns
from .main.controller.user_controller import api as user_ns
from .main.util.api_error import APIError
from .main.util.auth_utils import Auth

blueprint = Blueprint("api", __name__)

api = Api(blueprint,
          title="Institute API",
          prefix='/api/',
          version="X.Y.Z",
          description="API",
          security="apikey",
          authorizations=Auth,
          contact_email="joaobruno.rf@gmail.com",
          )

api.add_namespace(address_ns)
api.add_namespace(auth_ns, path="/auth")
api.add_namespace(document_ns, path="/document")
api.add_namespace(employee_ns, path="/employee")
api.add_namespace(error_ns, path="/error")
api.add_namespace(institute_ns, path="/institute")
api.add_namespace(student_ns, path="/student")
api.add_namespace(user_ns, path="/user")


@api.errorhandler(APIError)
@error_ns.marshal_with(_error_response)
def handle_default_exception(error):
    """
    Handles APIError and returns a formatted error response.

    Args:
        error (APIError): The exception to be handled.

    Returns:
        tuple: A tuple containing the formatted error response object and the corresponding HTTP status code.
    """
    if isinstance(error, APIError):
        return {"error": error.to_error()}, error.code
