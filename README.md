# BlogNest - RESTful Blog Application API

**Project ID**: `SCR845NGFF`  
**Organization**: InnoByte Services  
**Technology Stack**: Python / Flask, MongoDB (PyMongo), JWT Authentication  

---

## Overview

This repository contains the complete implementation of the **BlogNest RESTful Blog Application API**, developed according to the 25-Day Project Roadmap.

### Key Features
- **CRUD for Blog Posts**: Create, read (paginated), read single, update, and delete posts.
- **CRUD for Comments**: Create, read (filtered by `post_id`), read single, update, and delete comments.
- **Cascade Deletion**: Deleting a post automatically cascade-deletes all associated comments from MongoDB.
- **JWT Authentication & Authorization**: Secure user registration, login, and author-only access control.
- **Validation & Error Handling**: Comprehensive validation for usernames, emails, passwords, and object IDs.
- **Interactive Documentation**: Embedded **Swagger UI** (`/docs`), OpenAPI 3.0 specification (`/swagger.json`), and ready-to-import **Postman Collection** (`docs/postman_collection.json`).
- **Automated Test Suite**: Unit and integration tests covering all routes and security boundaries.

---

## Project Structure

```text
blog-application-api/
├── app/
│   ├── __init__.py          # Flask app factory, Swagger UI & error handlers
│   ├── config.py            # MongoDB environment configurations
│   ├── extensions.py        # MongoDB, JWT, CORS extensions
│   ├── models/              # MongoDB Document Repositories
│   │   ├── __init__.py
│   │   ├── user.py          # User collection repository & hashing
│   │   ├── post.py          # Post collection repository
│   │   └── comment.py       # Comment collection repository
│   ├── routes/              # API Blueprints
│   │   ├── __init__.py
│   │   ├── auth.py          # /register, /login, /me endpoints
│   │   ├── posts.py         # /posts CRUD endpoints
│   │   └── comments.py      # /comments CRUD endpoints
│   ├── schemas/             # Input payload validation
│   └── utils/               # Helpers & error formatters
├── tests/                   # Pytest test suite
│   ├── conftest.py          # Fixtures & in-memory Mongo test environment
│   ├── test_auth.py         # Authentication tests
│   ├── test_posts.py        # Post management tests
│   ├── test_comments.py     # Comment management tests
│   └── test_integration.py  # End-to-end integration test
├── docs/                    # Complete documentation
│   ├── api-specification.md # Detailed Markdown API documentation
│   ├── database-schema.md   # MongoDB schema, ER diagram & index setup
│   ├── swagger.json         # OpenAPI 3.0 specification
│   └── postman_collection.json # Exportable Postman collection
├── .env.example             # MongoDB environment template
├── requirements.txt         # Project dependencies
├── init_db.py               # MongoDB index & collection setup script
├── run.py                   # Application entry point
└── README.md                # Project documentation
```

---

## Quickstart

```powershell
# 1. Activate environment
.\.venv\Scripts\Activate.ps1

# 2. Setup environment variables
Copy-Item blog-application-api\.env.example blog-application-api\.env

# 3. Initialize MongoDB indexes
cd blog-application-api
python init_db.py

# 4. Start the API server
python run.py

# 5. Run tests
pytest
```

- API Base URL: `http://localhost:5000`
- Interactive Swagger UI: `http://localhost:5000/docs`
