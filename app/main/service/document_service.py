from .. import db
from ..util.api_error import APIError
from ..service.aws_service import upload_file_to_s3, view_file_from_s3, delete_file_from_s3
from ..service.email_service import send_email
from ..model import User, Document
from ..util.pagination_utils import paginate, get_document_filters
from ..util.document_validation_utils import validate_document


def upload_document_file(id: int, file, allowed_extensions: set[str]) -> str:
    """Upload a document file to Amazon S3 bucket.

    Args:
        id (int): ID of the document.
        file: File object to be uploaded.
        allowed_extensions (set[str]): Set of allowed file extensions.

    Returns:
        str: Key/Name of the uploaded file in the S3 bucket.

    Raises:
        APIError: If the file format is not supported or an error occurs during upload.
    """
    key = f"{id}.pdf"
    return upload_file_to_s3(key, file, allowed_extensions)


def save_document_file(student_id: int, document_file=None) -> str:
    """Save a document file for a student.

    Args:
        student_id (int): ID of the student.
        document_file: File object to be saved.

    Returns:
        str: Key/Name of the uploaded file in the S3 bucket.

    Raises:
        APIError: If no files are indexed to upload.
    """
    if document_file:
        file_key = upload_document_file(id=student_id, file=document_file, allowed_extensions={"pdf"})
        return file_key
    else:
        raise APIError("No files indexed to upload.", code=406, api_code="FILE_NOT_INDEXED")


def view_document_file(user: User):
    """Retrieve a document file from Amazon S3 bucket.

    Args:
        user (User): User object.

    Returns:
        object: File object from the S3 bucket.

    Raises:
        APIError: If the file is not found or an error occurs during retrieval.
    """
    key = f"{user.student.id}.pdf"
    return view_file_from_s3(key)


def delete_document_file(user: User):
    """Delete a document file from Amazon S3 bucket.

    Args:
        user (User): User object.

    Raises:
        APIError: If the file is not found or an error occurs during deletion.
    """
    view_document_file(user)
    key = f"{user.student.id}.pdf"
    return delete_file_from_s3(key)


def save_new_document(data, user: User, document_file=None, is_update=False):
    """Save a new document.

    Args:
        data: Document data.
        user (User): User object.
        document_file: File object to be saved.
        is_update (bool, optional): Whether it is an update operation. Defaults to False.

    Returns:
        Document: Newly created document.

    Raises:
        APIError: If the student doesn't exist, document already exists, or the document data is invalid.
    """
    if student := user.student:
        if not is_update and student.document:
            raise APIError("Document already exists", code=409)

        if info := validate_document(data):
            raise APIError(
                "Invalid JSON",
                code=400,
                api_code="INVALID_DOCUMENT",
                info=info
            )

        key = document_file and save_document_file(student.id, document_file)

        new_document = Document(
            title=data.get("title"),
            key=key,
            student_id=student.id,
        )
        if not is_update:
            save(new_document)

            send_email(
                email=user.email,
                template_name="DOCUMENT_UPLOAD_SUCCESSFULLY.html",
                message_subject="Document Upload Successfully",
            )

        return new_document
    raise APIError("Student doesn't exist.", code=404, api_code="STUDENT_NOT_FOUND")


def save(data: Document):
    """Save a document to the database.

    Args:
        data (Document): Document object to be saved.
    """
    db.session.add(data)
    db.session.commit()


def update_document(data, user: User, document_file=None):
    """Update a document.

    Args:
        data: Updated document data.
        user (User): User object.
        document_file: Updated file object.

    Returns:
        Document: Updated document.

    Raises:
        APIError: If the document doesn't exist, the document data is invalid, or an error occurs during the update.
    """
    if info := validate_document(data):
        raise APIError(
            "Invalid JSON",
            code=400,
            api_code="INVALID_DOCUMENT",
            info=info
        )

    if document := user.student.document:
        old_document_file = document.key and view_document_file(user)
        try:
            delete_document(user, is_update=True)
            new_document = save_new_document(data, user, document_file, is_update=True)
            db.session.add(new_document)

        except Exception as e:
            db.session.rollback()

            new_document_key = old_document_file and save_document_file(user.student.id, old_document_file)
            if new_document_key:
                document.key = new_document_key
                db.session.commit()

            raise APIError(
                "Document update failed.",
                code=400,
                api_code="DOCUMENT_UPDATE_FAILED",
                info=e.info if isinstance(e, APIError) else e,
            )

        else:
            db.session.commit()
            return new_document
    raise APIError("Document not found", code=404)


def get_document(user: User):
    """Get the document for a user.

    Args:
        user (User): User object.

    Returns:
        Document: User's document.

    Raises:
        APIError: If the document doesn't exist.
    """
    if document := user.student.document:
        return document
    raise APIError(
        "Document doesn't exist.",
        code=404,
        api_code="DOCUMENT_NOT_FOUND",
    )


def delete_document(user: User, is_update=False):
    """Delete a document.

    Args:
        user (User): User object.
        is_update (bool, optional): Whether it is an update operation. Defaults to False.

    Raises:
        APIError: If the document doesn't exist or an error occurs during deletion.
    """
    document = get_document(user)
    db.session.delete(document)
    if not is_update:
        if document.key:
            delete_document_file(user)
        db.session.commit()


def get_all_documents(user: User):
    """Get all documents.

    Args:
        user (User): User object.

    Returns:
        Pagination: Paginated list of documents.

    Raises:
        APIError: If an error occurs during pagination.
    """
    documents_filter = get_document_filters()

    return paginate(
        Document,
        filter=documents_filter
    )
