import os
import json
from flask import Flask, jsonify, render_template_string, render_template, request
from app.config import config_by_name
from app.extensions import mongo, jwt, cors


SWAGGER_UI_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>BlogNest API - Swagger Documentation</title>
  <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5.11.0/swagger-ui.css" />
  <style>
    body { margin: 0; background: #fafafa; }
    .topbar { display: none !important; }
  </style>
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://unpkg.com/swagger-ui-dist@5.11.0/swagger-ui-bundle.js"></script>
  <script>
    window.onload = () => {
      window.ui = SwaggerUIBundle({
        url: '/swagger.json',
        dom_id: '#swagger-ui',
        deepLinking: true,
        presets: [
          SwaggerUIBundle.presets.apis,
          SwaggerUIBundle.SwaggerUIStandalonePreset
        ],
        layout: "BaseLayout"
      });
    };
  </script>
</body>
</html>
"""


def create_app(config_name=None):
    """Application factory for BlogNest RESTful Blog API (Project SCR845NGFF)."""
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    template_dir = os.path.join(os.path.dirname(__file__), "templates")
    app = Flask(__name__, template_folder=template_dir)
    app.config.from_object(config_by_name.get(config_name, config_by_name["default"]))

    # Initialize extensions
    mongo.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)

    # Register blueprints
    from app.routes import auth_bp, posts_bp, comments_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(posts_bp)
    app.register_blueprint(comments_bp)

    # Root route: serves frontend web application to browser, JSON to API clients
    @app.route("/", methods=["GET"])
    def root():
        best = request.accept_mimetypes.best_match(["text/html", "application/json"])
        if best == "application/json" and request.accept_mimetypes[best] > request.accept_mimetypes["text/html"]:
            return jsonify({
                "project_id": "SCR845NGFF",
                "name": "BlogNest RESTful Blog Application API",
                "status": "online",
                "database": "MongoDB",
                "frontend": "/",
                "documentation": "/docs",
                "openapi_spec": "/swagger.json"
            }), 200
        return render_template("index.html")

    # API health check endpoint
    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify({
            "status": "healthy",
            "project_id": "SCR845NGFF",
            "service": "BlogNest MongoDB API",
            "database_mode": "in-memory-preview" if mongo.is_fallback else "live-mongodb"
        }), 200

    # Interactive Swagger UI Documentation
    @app.route("/docs", methods=["GET"])
    def swagger_ui():
        return render_template_string(SWAGGER_UI_TEMPLATE)

    @app.route("/swagger.json", methods=["GET"])
    def swagger_json():
        docs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs")
        spec_path = os.path.join(docs_dir, "swagger.json")
        if os.path.exists(spec_path):
            with open(spec_path, "r", encoding="utf-8") as f:
                return jsonify(json.load(f))
        return jsonify({"error": "Swagger specification file not found."}), 404

    # Global error handlers
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"error": "Bad request"}), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({"error": "Unauthorized"}), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({"error": "Forbidden"}), 403

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal server error"}), 500

    return app
