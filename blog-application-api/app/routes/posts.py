import math
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.post import Post
from app.models.comment import Comment
from app.schemas.validators import validate_post_payload
from app.utils.helpers import error_response, success_response, is_valid_object_id

posts_bp = Blueprint("posts", __name__)


@posts_bp.route("/posts", methods=["GET"])
@posts_bp.route("/api/posts", methods=["GET"])
def get_posts():
    """Read all blog posts with pagination and optional author filtering."""
    try:
        page = max(1, int(request.args.get("page", 1)))
        per_page = max(1, min(100, int(request.args.get("per_page", 10))))
    except ValueError:
        return error_response("Invalid pagination parameters.", 400)

    author_id = request.args.get("author_id", type=str)
    filter_query = {}
    if author_id:
        filter_query["author_id"] = str(author_id)

    total = Post.count(filter_query)
    skip = (page - 1) * per_page
    posts_list = Post.find(filter_query, skip=skip, limit=per_page)
    pages = math.ceil(total / per_page) if total > 0 else 1

    return success_response(
        data={"posts": [Post.to_dict(p) for p in posts_list]},
        page=page,
        per_page=per_page,
        total=total,
        pages=pages,
        status_code=200,
    )


@posts_bp.route("/posts/<string:post_id>", methods=["GET"])
@posts_bp.route("/api/posts/<string:post_id>", methods=["GET"])
def get_post(post_id: str):
    """Read single blog post by ID along with its associated comments."""
    if not is_valid_object_id(post_id):
        return error_response("Invalid post ID format.", 400)

    post_doc = Post.find_by_id(post_id)
    if not post_doc:
        return error_response("Post not found.", 404)

    post_data = Post.to_dict(post_doc)
    comments_list = Comment.find({"post_id": str(post_id)})
    post_data["comments"] = [Comment.to_dict(c) for c in comments_list]

    return success_response(data={"post": post_data}, status_code=200)


@posts_bp.route("/posts", methods=["POST"])
@posts_bp.route("/api/posts", methods=["POST"])
@jwt_required()
def create_post():
    """Create a new blog post (Authenticated users only)."""
    current_user_id = str(get_jwt_identity())
    data = request.get_json(silent=True) or {}

    is_valid, err_msg = validate_post_payload(data, is_update=False)
    if not is_valid:
        return error_response(err_msg, 400)

    post_doc = Post.create(
        title=str(data["title"]).strip(),
        content=str(data["content"]).strip(),
        author_id=current_user_id,
    )

    return success_response(
        data={"post": Post.to_dict(post_doc)},
        message="Post created successfully.",
        status_code=201,
    )


@posts_bp.route("/posts/<string:post_id>", methods=["PUT"])
@posts_bp.route("/api/posts/<string:post_id>", methods=["PUT"])
@jwt_required()
def update_post(post_id: str):
    """Update an existing post (Author only)."""
    if not is_valid_object_id(post_id):
        return error_response("Invalid post ID format.", 400)

    current_user_id = str(get_jwt_identity())
    post_doc = Post.find_by_id(post_id)
    if not post_doc:
        return error_response("Post not found.", 404)

    if str(post_doc.get("author_id")) != current_user_id:
        return error_response("Unauthorized: You can only update your own posts.", 403)

    data = request.get_json(silent=True) or {}
    is_valid, err_msg = validate_post_payload(data, is_update=True)
    if not is_valid:
        return error_response(err_msg, 400)

    updates = {}
    if "title" in data:
        updates["title"] = str(data["title"]).strip()
    if "content" in data:
        updates["content"] = str(data["content"]).strip()

    if not updates:
        return error_response("No valid fields provided for update.", 400)

    updated_doc = Post.update_by_id(post_id, updates)
    return success_response(
        data={"post": Post.to_dict(updated_doc)},
        message="Post updated successfully.",
        status_code=200,
    )


@posts_bp.route("/posts/<string:post_id>", methods=["DELETE"])
@posts_bp.route("/api/posts/<string:post_id>", methods=["DELETE"])
@jwt_required()
def delete_post(post_id: str):
    """Delete a post and its comments (Author only)."""
    if not is_valid_object_id(post_id):
        return error_response("Invalid post ID format.", 400)

    current_user_id = str(get_jwt_identity())
    post_doc = Post.find_by_id(post_id)
    if not post_doc:
        return error_response("Post not found.", 404)

    if str(post_doc.get("author_id")) != current_user_id:
        return error_response("Unauthorized: You can only delete your own posts.", 403)

    Post.delete_by_id(post_id)
    return success_response(message="Post deleted successfully.", status_code=200)
