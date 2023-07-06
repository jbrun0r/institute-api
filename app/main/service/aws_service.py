from ..config import StagingConfig
from ..util.api_error import APIError
from botocore.exceptions import ClientError

bucket_name = StagingConfig.AWS_S3_BUCKET
s3_client = StagingConfig.S3
s3_client_client = StagingConfig.CLIENT


def is_allowed_file(filename: str, allowed_extensions: set[str]) -> bool:
    """Check if the file extension is allowed.

    Args:
        filename (str): Name of the file.
        allowed_extensions (set[str]): Set of allowed file extensions.

    Returns:
        bool: True if the file extension is allowed, False otherwise.
    """
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


def upload_file_to_s3(key: str, file, allowed_extensions: set[str]) -> str:
    """Upload a file to Amazon S3 bucket.

    Args:
        key (str): Key/Name of the file in the S3 bucket.
        file: File object to be uploaded.
        allowed_extensions (set[str]): Set of allowed file extensions.

    Returns:
        str: Key/Name of the uploaded file in the S3 bucket.

    Raises:
        APIError: If the file format is not supported or an error occurs during upload.
    """
    if is_allowed_file(file.filename, allowed_extensions):
        try:
            file_data = file.stream.read()
            response = s3_client.Bucket(bucket_name).put_object(Key=key, Body=file_data)
            return response.key
        except ClientError as e:
            raise APIError("Upload error.", code=400, info=e, api_code="S3_INTERNAL_ERROR")
    else:
        raise APIError("Unsupported file format.", code=415, api_code="UNSUPPORTED_FILE")


def view_file_from_s3(key: str):
    """Retrieve a file from Amazon S3 bucket.

    Args:
        key (str): Key/Name of the file in the S3 bucket.

    Returns:
        object: File object from the S3 bucket.

    Raises:
        APIError: If the file is not found or an error occurs during retrieval.
    """
    try:
        return s3_client_client.get_object(Bucket=bucket_name, Key=key)
    except ClientError as e:
        raise APIError("File not found.", code=404, info=e)


def delete_file_from_s3(key: str):
    """Delete a file from Amazon S3 bucket.

    Args:
        key (str): Key/Name of the file in the S3 bucket.

    Returns:
        dict: Response data from S3 indicating the deletion.

    Raises:
        APIError: If the file is not found or an error occurs during deletion.
    """
    try:
        view_file_from_s3(key)
        return s3_client_client.delete_object(Bucket=bucket_name, Key=key)
    except ClientError as e:
        raise APIError("Unable to delete uploaded file as it was not found.", code=404, info=e, api_code="FILE_DELETE_FAILED")
