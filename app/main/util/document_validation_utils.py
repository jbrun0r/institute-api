from json import loads

def validate_title(title: str) -> str:
    """
    Validates the document title.

    Args:
        title (str): The title to validate.

    Returns:
        str: An error message if the title is invalid, None otherwise.
    """
    if not isinstance(title, str):
        return "'title' is not a string"
    if len(title) > 100:
        return f"Title is too long ({len(title)} characters, 100 is the limit)"

def validate_document(data: dict[str, any]) -> dict[str, str]:
    """
    Validates the document fields.

    Args:
        data (dict[str, any]): The document data to validate.

    Returns:
        dict[str, str]: A dictionary describing the errors found.
    """
    FIELDS_VALIDATORS = {"title": validate_title}
    REQUIRED_FIELDS = ["title"]
    error_info = {}

    for field in REQUIRED_FIELDS:
        if field not in data:
            error_info[field] = "Required field is missing"

    for field, validator in FIELDS_VALIDATORS.items():
        if field in data and (error := validator(data[field])):
            error_info[field] = error

    return error_info

def parse_request_value(value) -> dict:
    """
    Parses the request value or raises a ValueError.

    Args:
        value: The value to parse.

    Returns:
        dict: The parsed value.

    Raises:
        ValueError: If the value cannot be parsed.
    """
    return loads(value)
