from .. import db
from .api_error import APIError

from flask import request, current_app
from sqlalchemy.sql import text


def get_paginate_parameters() -> dict[str, int]:
    """
    Get the pagination parameters from the request arguments.

    Returns:
        dict[str, int]: The pagination parameters.
    """
    return {
        "page": request.args.get("page", 1, type=int),
        "per_page": request.args.get("per_page", 2, type=int),
        "max_per_page": 10,
    }


def get_ordering_parameters(ordenable_columns: list, tables: list) -> list:
    """
    Get the ordering parameters from the request arguments.

    Args:
        ordenable_columns (list): The columns that can be ordered.
        tables (list): The tables to consider when ordering.

    Returns:
        list: The ordering parameters.

    Raises:
        APIError: If an invalid column is provided for ordering.
    """
    sort_data = {}
    if sort := request.args.get("sort", [], lambda string: string.split(",")):
        for name in sort:
            col_name = name.removeprefix("-")
            table_with_col = next(filter(lambda table: hasattr(table, col_name), tables), False)

            if col_name in ordenable_columns and table_with_col:
                sort_data[getattr(table_with_col, col_name)] = 'desc' if name.startswith("-") else 'asc'
            else:
                raise APIError(
                    "Invalid column to order",
                    code=400,
                    api_code="INVALID_ORDERING_COLUMN",
                    info=f"Unable to order by '{col_name}'",
                )
    return [getattr(column, order)() for column, order in sort_data.items()]


def paginate(table, *joinable_tables, filter: list, ordenable_columns: list = []):
    """
    Paginate the results based on the provided parameters.

    Args:
        table: The main table to paginate.
        joinable_tables: The additional tables to join.
        filter (list): The filters to apply.
        ordenable_columns (list, optional): The columns that can be ordered. Defaults to [].

    Returns:
        Pagination: The paginated results.

    Raises:
        APIError: If no page is generated.
    """
    paginate_kwargs = get_paginate_parameters()

    query = db.session.query(table)
    for sub_table in joinable_tables:
        query = query.join(sub_table)

    filtered = query.filter(*filter)
    if clauses := get_ordering_parameters(ordenable_columns, [table] + list(joinable_tables)):
        filtered = filtered.order_by(*clauses)

    pagination = filtered.paginate(**paginate_kwargs)
    if pagination.items:
        pagination.limit = paginate_kwargs["max_per_page"]
        return pagination
    raise APIError("No page generated", code=404, api_code="PAGES_NOT_FOUND")


def get_student_filters() -> list:
    """
    Get the filters for querying students.

    Returns:
        list: The student filters.
    """
    student_filter = []
    operator = "ILIKE"
    case = ""
    args_list = [
        "name",
        "state",
        "city",
    ]

    if "sqlite" in current_app.config["SQLALCHEMY_DATABASE_URI"]:
        operator = "LIKE"
        case = "COLLATE NOCASE"

    for arg in args_list:
        if value := request.args.get(arg, default=None, type=str):
            student_filter.append(text(f"{arg} {operator} '%{value}%' {case}"))

    if gender := request.args.get("gender", default=None, type=str):
        student_filter.append(text(f"gender = '{gender}' {case}"))

    if date_lower := request.args.get("date_lower", default=None, type=str):
        if date_upper := request.args.get("date_upper", default=None, type=str):
            student_filter.append(
                text(f"birthday_date BETWEEN '{date_lower}' AND '{date_upper}'")
            )

    return student_filter


def get_document_filters() -> list:
    """
    Get the filters for querying documents.

    Returns:
        list: The document filters.
    """
    document_filter = []
    operator = "ILIKE"
    case = ""
    args_list = ["title"]

    if "sqlite" in current_app.config["SQLALCHEMY_DATABASE_URI"]:
        operator = "LIKE"
        case = "COLLATE NOCASE"

    for arg in args_list:
        if value := request.args.get(arg, default=None, type=str):
            document_filter.append(text(f"{arg} {operator} '%{value}%' {case}"))

    return document_filter


def get_institute_filters() -> list:
    """
    Get the filters for querying institutes.

    Returns:
        list: The institute filters.
    """
    institute_filter = []
    operator = "ILIKE"
    case = ""
    args_list = ["trading_name", "corporate_name", "state", "city", "cnpj", "state_registration"]

    if "sqlite" in current_app.config["SQLALCHEMY_DATABASE_URI"]:
        operator = "LIKE"
        case = "COLLATE NOCASE"

    for arg in args_list:
        if value := request.args.get(arg, default=None, type=str):
            institute_filter.append(text(f"{arg} {operator} '%{value}%' {case}"))

    return institute_filter


def get_error_filters() -> list:
    """
    Get the filters for querying errors.

    Returns:
        list: The error filters.
    """
    error_filter = []
    operator = "ILIKE"
    case = ""
    args_list = [
        "code",
        "api_code",
        "description",
    ]

    if "sqlite" in current_app.config["SQLALCHEMY_DATABASE_URI"]:
        operator = "LIKE"
        case = "COLLATE NOCASE"

    for arg in args_list:
        if value := request.args.get(arg, default=None, type=str):
            error_filter.append(text(f"{arg} {operator} '%{value}%' {case}"))

    return error_filter


def get_user_filters() -> list:
    """
    Get the filters for querying users.

    Returns:
        list: The user filters.
    """
    user_filter = []
    operator = "ILIKE"
    case = ""

    if "sqlite" in current_app.config["SQLALCHEMY_DATABASE_URI"]:
        operator = "LIKE"
        case = "COLLATE NOCASE"

    if value := request.args.get("search", default=None, type=str):
        user_filter.append(text(f"(name {operator} '%{value}%' {case} OR email {operator} '%{value}%' {case})"))

    if profile := request.args.get("profile", default=None, type=str):
        user_filter.append(text(f"profile = '{profile}'"))

    return user_filter
