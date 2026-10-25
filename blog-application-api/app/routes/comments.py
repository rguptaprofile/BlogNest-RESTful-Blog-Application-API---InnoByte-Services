import math
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.post import Post
from app.models.comment import Comment
from app.schemas.validators import validate_comment_payload
from app.utils.helpers import error_response, success_response, is_valid_object_id

comments_bp = Blueprint("comments", __name__)


@comments_bp.route("/comments", methods=["GET"])
@comments_bp.route("/api/comments", methods=["GET"])
def get_comments():
    """Read comments with optional post_id or author_id filtering."""
    try:
        page = max(1, int(request.args.get("page", 1)))
        per_page = max(1, min(100, int(request.args.get("per_page", 20))))
    except ValueError:
        return error_response("Invalid pagination parameters.", 400)

    post_id = request.args.get("post_id", type=str)
    author_id = request.args.get("author_id", type=str)

    filter_query = {}
    if post_id:
        filter_query["post_id"] = str(post_id)
    if author_id:
        filter_query["author_id"] = str(author_id)

    total = Comment.count(filter_query)
    skip = (page - 1) * per_page
    comments_list = Comment.find(filter_query, skip=skip, limit=per_page)
    pages = math.ceil(total / per_page) if total > 0 else 1

    return success_response(
        data={"comments": [Comment.to_dict(c) for c in comments_list]},
        page=page,
        per_page=per_page,
        total=total,
        pages=pages,
        status_code=200,
    )


@comments_bp.route("/comments/<string:comment_id>", methods=["GET"])
@comments_bp.route("/api/comments/<string:comment_id>", methods=["GET"])
def get_comment(comment_id: str):
    """Read single comment by ID."""
    if not is_valid_object_id(comment_id):
        return error_response("Invalid comment ID format.", 400)

    comment_doc = Comment.find_by_id(comment_id)
    if not comment_doc:
        return error_response("Comment not found.", 404)

    return success_response(data={"comment": Comment.to_dict(comment_doc)}, status_code=200)


@comments_bp.route("/comments", methods=["POST"])
@comments_bp.route("/api/comments", methods=["POST"])
@jwt_required()
def create_comment():
    """Create a new comment on a post (Authenticated users only)."""
    current_user_id = str(get_jwt_identity())
    data = request.get_json(silent=True) or {}

    is_valid, err_msg = validate_comment_payload(data, is_update=False)
    if not is_valid:
        return error_response(err_msg, 400)

    post_id = str(data["post_id"])
    if not Post.find_by_id(post_id):
        return error_response("Post not found.", 404)

    comment_doc = Comment.create(
        post_id=post_id,
        content=str(data["content"]).strip(),
        author_id=current_user_id,
    )

    return success_response(
        data={"comment": Comment.to_dict(comment_doc)},
        message="Comment created successfully.",
        status_code=201,
    )


@comments_bp.route("/comments/<string:comment_id>", methods=["PUT"])
@comments_bp.route("/api/comments/<string:comment_id>", methods=["PUT"])
@jwt_required()
def update_comment(comment_id: str):
    """Update a comment (Author only)."""
    if not is_valid_object_id(comment_id):
        return error_response("Invalid comment ID format.", 400)

    current_user_id = str(get_jwt_identity())
    comment_doc = Comment.find_by_id(comment_id)
    if not comment_doc:
        return error_response("Comment not found.", 404)

    if str(comment_doc.get("author_id")) != current_user_id:
        return error_response("Unauthorized: You can only update your own comments.", 403)

    data = request.get_json(silent=True) or {}
    is_valid, err_msg = validate_comment_payload(data, is_update=True)
    if not is_valid:
        return error_response(err_msg, 400)

    new_content = str(data.get("content", "")).strip()
    if not new_content:
        return error_response("Content cannot be empty.", 400)

    updated_doc = Comment.update_by_id(comment_id, {"content": new_content})
    return success_response(
        data={"comment": Comment.to_dict(updated_doc)},
        message="Comment updated successfully.",
        status_code=200,
    )


@comments_bp.route("/comments/<string:comment_id>", methods=["DELETE"])
@comments_bp.route("/api/comments/<string:comment_id>", methods=["DELETE"])
@jwt_required()
def delete_comment(comment_id: str):
    """Delete a comment (Author only)."""
    if not is_valid_object_id(comment_id):
        return error_response("Invalid comment ID format.", 400)

    current_user_id = str(get_jwt_identity())
    comment_doc = Comment.find_by_id(comment_id)
    if not comment_doc:
        return error_response("Comment not found.", 404)

    if str(comment_doc.get("author_id")) != current_user_id:
        return error_response("Unauthorized: You can only delete your own comments.", 403)

    Comment.delete_by_id(comment_id)
    return success_response(message="Comment deleted successfully.", status_code=200)


# ---------------------------------------------------------
# Nested convenience endpoints: /posts/<post_id>/comments
# ---------------------------------------------------------

@comments_bp.route("/posts/<string:post_id>/comments", methods=["GET"])
@comments_bp.route("/api/posts/<string:post_id>/comments", methods=["GET"])
def get_post_comments(post_id: str):
    """Read all comments directly for a specific post."""
    if not is_valid_object_id(post_id) or not Post.find_by_id(post_id):
        return error_response("Post not found.", 404)

    comments_list = Comment.find({"post_id": str(post_id)})
    return success_response(
        data={"comments": [Comment.to_dict(c) for c in comments_list]},
        status_code=200,
    )


@comments_bp.route("/posts/<string:post_id>/comments", methods=["POST"])
@comments_bp.route("/api/posts/<string:post_id>/comments", methods=["POST"])
@jwt_required()
def add_post_comment(post_id: str):
    """Add a comment directly under a post."""
    if not is_valid_object_id(post_id) or not Post.find_by_id(post_id):
        return error_response("Post not found.", 404)

    current_user_id = str(get_jwt_identity())
    data = request.get_json(silent=True) or {}
    content = str(data.get("content", "")).strip()

    if not content:
        return error_response("Comment content is required.", 400)

    comment_doc = Comment.create(
        post_id=str(post_id),
        content=content,
        author_id=current_user_id,
    )
    return success_response(
        data={"comment": Comment.to_dict(comment_doc)},
        message="Comment created successfully.",
        status_code=201,
    )
