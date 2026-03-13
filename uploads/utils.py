# uploads/utils.py
import hashlib


def calculate_md5(file_obj):
    """
    Calculates MD5 hash of an uploaded file object.
    """
    md5_hash = hashlib.md5()
    for chunk in file_obj.chunks():
        md5_hash.update(chunk)
    return md5_hash.hexdigest()


ALLOWED_EXTENSIONS = ["pdf", "txt", "png", "jpg", "jpeg", "gif"]
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def validate_file(file_obj, max_size=MAX_FILE_SIZE, allowed_types=None):
    """
    Validates uploaded file:
    - max_size in bytes (default 10 MB)
    - allowed_types is a list of MIME types
    """
    if file_obj.size > max_size:
        raise ValueError(f"File is too large. Max size is {max_size} bytes.")

    if allowed_types:
        if file_obj.content_type not in allowed_types:
            raise ValueError(f"File type {file_obj.content_type} is not allowed.")
