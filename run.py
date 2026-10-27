"""BlogNest — RESTful Blog Application API Server Runner.

Project ID: SCR845NGFF
Usage:
    python run.py
"""
import os
import sys

# Ensure application package is discoverable from both root and subfolder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(BASE_DIR, "blog-application-api")
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from app import create_app

app = create_app(os.getenv("FLASK_ENV", "development"))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1")
    print("\n" + "=" * 62)
    print("  BlogNest RESTful Blog Application API (Project SCR845NGFF)")
    print(f"  Live Server:          http://127.0.0.1:{port}")
    print(f"  Interactive Swagger:  http://127.0.0.1:{port}/docs")
    print(f"  OpenAPI Spec:         http://127.0.0.1:{port}/swagger.json")
    print(f"  Editorial Web App:    http://127.0.0.1:{port}")
    print("=" * 62 + "\n")
    app.run(host="0.0.0.0", port=port, debug=debug)
