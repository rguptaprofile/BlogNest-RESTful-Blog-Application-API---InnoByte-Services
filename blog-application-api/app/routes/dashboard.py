"""Dashboard & Analytics Routes.

Exposes authenticated and platform analytics calculated entirely in Python.
"""
from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.dashboard_service import DashboardService
from app.utils.helpers import success_response, error_response

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/api/dashboard/me", methods=["GET"])
@dashboard_bp.route("/dashboard/me", methods=["GET"])
@dashboard_bp.route("/api/dashboard", methods=["GET"])
@dashboard_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def get_my_dashboard():
    """Retrieve comprehensive server-computed dashboard metrics for authenticated author."""
    user_id = get_jwt_identity()
    dashboard_data = DashboardService.get_user_dashboard(user_id)
    if not dashboard_data:
        return error_response("User profile not found.", 404)

    return success_response(
        data={"dashboard": dashboard_data},
        message="User dashboard metrics computed successfully.",
        status_code=200
    )


@dashboard_bp.route("/api/dashboard/platform", methods=["GET"])
@dashboard_bp.route("/dashboard/platform", methods=["GET"])
def get_platform_metrics():
    """Retrieve global platform-wide statistics computed in Python."""
    metrics = DashboardService.get_platform_metrics()
    return success_response(
        data={"platform": metrics},
        message="Platform metrics retrieved successfully.",
        status_code=200
    )
