import re
from app.utils.helpers import is_valid_object_id

EMAIL_REGEX = re.compile(r"^[\w\.-]+@([\w-]+\.)+[\w-]{2,4}$")
USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_]{3,30}$")


def validate_registration_payload(data: dict):
    if not isinstance(data, dict):
        return False, "Request body must be a valid JSON object."

    username = str(data.get("username", "")).strip()
    email = str(data.get("email", "")).strip()
    password = str(data.get("password", ""))

    if not username:
        return False, "Username is required."
    if not USERNAME_REGEX.match(username):
        return False, "Username must be 3-30 characters long and contain only letters, numbers, or underscores."

    if not email:
        return False, "Email is required."
    if not EMAIL_REGEX.match(email):
        return False, "Invalid email format."

    if not password:
        return False, "Password is required."
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."

    return True, None


def validate_login_payload(data: dict):
    if not isinstance(data, dict):
        return False, "Request body must be a valid JSON object."

    email = str(data.get("email", "")).strip()
    password = str(data.get("password", ""))

    if not email or not password:
        return False, "Email and password are required."

    return True, None


def validate_post_payload(data: dict, is_update: bool = False):
    if not isinstance(data, dict):
        return False, "Request body must be a valid JSON object."

    if not is_update:
        title = str(data.get("title", "")).strip()
        content = str(data.get("content", "")).strip()

        if not title:
            return False, "Title is required."
        if len(title) > 255:
            return False, "Title must not exceed 255 characters."
        if not content:
            return False, "Content is required."
    else:
        if "title" in data:
            title = str(data.get("title", "")).strip()
            if not title:
                return False, "Title cannot be empty."
            if len(title) > 255:
                return False, "Title must not exceed 255 characters."
        if "content" in data:
            content = str(data.get("content", "")).strip()
            if not content:
                return False, "Content cannot be empty."

    return True, None


def validate_comment_payload(data: dict, is_update: bool = False):
    if not isinstance(data, dict):
        return False, "Request body must be a valid JSON object."

    if not is_update:
        post_id = data.get("post_id")
        content = str(data.get("content", "")).strip()

        if not post_id:
            return False, "post_id is required."
        if not is_valid_object_id(post_id):
            return False, "Invalid post_id format."
        if not content:
            return False, "Comment content is required."
    else:
        if "content" in data:
            content = str(data.get("content", "")).strip()
            if not content:
                return False, "Comment content cannot be empty."

    return True, None
