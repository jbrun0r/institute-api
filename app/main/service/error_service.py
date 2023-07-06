from ..model import Error
from ..util.pagination_utils import get_error_filters, paginate


def get_filtered_errors():
    """
    Get a paginated list of filtered errors.

    Returns:
        Pagination: Paginated list of Error objects.
    """
    errors_filter = get_error_filters()
    return paginate(table=Error, filter=errors_filter)
