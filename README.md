# BlogNest — RESTful Blog Application API & Web Platform

**BlogNest** is a full-featured, high-performance blogging application and RESTful API built with **Python (Flask)**, **MongoDB (PyMongo)**, and **JWT Authentication**. It features an elegant Medium-inspired frontend UI, complete CRUD capabilities for posts and comments, cascade deletions, robust input validation, and interactive OpenAPI / Swagger documentation.

---

## Key Features

- **Blog Post Management**: Full CRUD operations with server-side pagination, search, and author filtering.
- **Interactive Commenting System**: Add, view, update, and delete comments on any story with real-time feedback.
- **Relational Integrity & Cascade Deletion**: Deleting a post automatically cleans up all associated comments from MongoDB.
- **JWT Authentication & Role-Based Access Control**: Secure token-based authentication (`/register`, `/login`, `/me`) ensuring only authors can edit or delete their own posts and comments.
- **Modern Editorial Web Frontend**: Responsive, distraction-free reading and writing interface built with pure vanilla JS and Tailwind CSS, featuring reading time estimates, topic filtering, claps, and live word counter.
- **Embedded API Documentation**: Interactive Swagger UI playground available at `/docs`, raw OpenAPI 3.0 specification at `/swagger.json`, and ready-to-import Postman collection.
- **Automated Test Coverage**: Comprehensive test suite using `pytest` verifying unit functionality and end-to-end integration workflows.

---

## Technology Stack

| Component | Technology | Description |
|---|---|---|
| **Backend Framework** | Python 3.10+ / Flask | Lightweight, modular WSGI web application |
| **Database** | MongoDB / PyMongo | Document-oriented NoSQL database with indexed collections |
| **Authentication** | Flask-JWT-Extended | Stateless JSON Web Token authentication with Bearer tokens |
| **Security** | Werkzeug Security | Password hashing with secure cryptographic algorithms |
| **Frontend UI** | HTML5 / Tailwind CSS / Vanilla JS | Editorial design with zero build-step overhead |
| **Documentation** | Swagger UI / OpenAPI 3.0 | Interactive API documentation playground |
| **Testing** | Pytest / Pytest-Flask | Automated unit and integration test runner |

---

## Project Structure

```text
BlogNest-RESTful-Blog-Application-API---InnoByte-Services/
├── blog-application-api/
│   ├── app/
│   │   ├── __init__.py          # Flask app factory, Swagger UI & route binding
│   │   ├── config.py            # MongoDB and JWT configuration profiles
│   │   ├── extensions.py        # MongoDB client wrapper, JWT, and CORS setup
│   │   ├── models/              # MongoDB Document Repositories
│   │   │   ├── __init__.py
│   │   │   ├── user.py          # User collection repository & password hashing
│   │   │   ├── post.py          # Blog post collection repository & cascade rules
│   │   │   └── comment.py       # Comment collection repository
│   │   ├── routes/              # API Blueprints
│   │   │   ├── __init__.py
│   │   │   ├── auth.py          # /register, /login, /me endpoints
│   │   │   ├── posts.py         # /posts CRUD endpoints
│   │   │   └── comments.py      # /comments CRUD endpoints
│   │   ├── schemas/             # Input payload validation functions
│   │   │   └── validators.py
│   │   ├── templates/           # Frontend Web Application template
│   │   │   └── index.html
│   │   └── utils/               # Helper utilities & standardized responses
│   │       └── helpers.py
│   ├── docs/                    # API Documentation & Schema
│   │   ├── api-specification.md # RESTful endpoints specification
│   │   ├── database-schema.md   # MongoDB collections, indexes, & ER diagram
│   │   ├── swagger.json         # OpenAPI 3.0 specification
│   │   └── postman_collection.json # Exportable Postman collection
│   ├── frontend/                # Standalone frontend copy
│   │   └── index.html
│   ├── tests/                   # Pytest automated test suite
│   │   ├── conftest.py          # Test fixtures and in-memory test backend
│   │   ├── test_auth.py         # Authentication test cases
│   │   ├── test_posts.py        # Blog post CRUD tests
│   │   ├── test_comments.py     # Comment management tests
│   │   └── test_integration.py  # End-to-end integration lifecycle test
│   ├── .env.example             # Environment variables configuration template
│   ├── init_db.py               # MongoDB index & collection setup script
│   ├── requirements.txt         # Project dependencies
│   └── run.py                   # Application entry point
├── .gitignore                   # Git ignore patterns
├── pytest.ini                   # Pytest configuration
├── LICENSE                      # MIT License
└── README.md                    # Project documentation
```

---

## Getting Started

### 1. Prerequisites
- **Python 3.10+**
- **MongoDB** (Local instance at `mongodb://localhost:27017` or a free MongoDB Atlas cloud cluster)

### 2. Environment Setup
Clone the repository and activate the virtual environment:

```powershell
# In PowerShell (Windows):
.\.venv\Scripts\Activate.ps1

# (Or in Linux/macOS):
source .venv/bin/activate
```

Create your `.env` configuration file:

```powershell
Copy-Item blog-application-api\.env.example blog-application-api\.env
```

Ensure your MongoDB connection string in `blog-application-api/.env` is set:
```env
MONGO_URI=mongodb://localhost:27017/blognest_db
MONGO_DBNAME=blognest_db
SECRET_KEY=change-this-to-a-super-secret-key-blognest
JWT_SECRET_KEY=change-this-to-a-jwt-secret-key-at-least-32-bytes
```

### 3. Initialize MongoDB Collections & Indexes
Run the initialization script to automatically create unique indexes for users (`username`, `email`), posts (`author_id`, `created_at`), and comments (`post_id`, `author_id`):

```powershell
cd blog-application-api
python init_db.py
```

### 4. Run the Application
Start the Flask development server:

```powershell
python run.py
```

- **Frontend Web Application**: [http://localhost:5000](http://localhost:5000)
- **Interactive Swagger Documentation**: [http://localhost:5000/docs](http://localhost:5000/docs)
- **OpenAPI 3.0 Specification**: [http://localhost:5000/swagger.json](http://localhost:5000/swagger.json)

---

## API Reference

All protected endpoints require the JWT access token passed in the `Authorization` header:
`Authorization: Bearer <token>`

### 1. Authentication
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/register` | Register a new user account | No |
| `POST` | `/login` | Authenticate user & receive JWT token | No |
| `GET` | `/me` | Fetch authenticated user profile | Yes |

### 2. Blog Posts
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/posts` | Read paginated posts (`?page=1&per_page=10&author_id=...`) | No |
| `GET` | `/posts/{id}` | Read single post and its populated comments | No |
| `POST` | `/posts` | Create a new blog post | Yes |
| `PUT` | `/posts/{id}` | Update an existing post (Author only) | Yes |
| `DELETE` | `/posts/{id}` | Delete a post & cascade-delete its comments (Author only) | Yes |

### 3. Comments
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/comments` | Read comments (`?post_id=...&author_id=...&page=1`) | No |
| `GET` | `/comments/{id}` | Read single comment by ID | No |
| `POST` | `/comments` | Create comment on a post (`post_id`, `content`) | Yes |
| `PUT` | `/comments/{id}` | Update a comment (Author only) | Yes |
| `DELETE` | `/comments/{id}` | Delete a comment (Author only) | Yes |
| `GET` | `/posts/{id}/comments` | Read all comments directly under a post | No |
| `POST` | `/posts/{id}/comments` | Add comment directly under a post | Yes |

*(Note: Prefixed aliases such as `/api/posts`, `/api/comments`, and `/api/auth/register` are also fully supported).*

---

## Testing & Quality Assurance

Run the comprehensive automated test suite with `pytest`:

```powershell
pytest
```

The test suite runs against a fast in-memory mock MongoDB backend and validates:
- User registration and login validation
- Duplicate username/email prevention (409 Conflict)
- Post creation, retrieval, updates, and deletion
- Comment creation, query filtering by `post_id`, and updates
- Role-based permissions (verifying that non-authors receive 403 Forbidden on edits/deletions)
- End-to-end integration lifecycle test verifying automatic comment cascade deletion when a post is removed

---

## Postman Collection

Import `blog-application-api/docs/postman_collection.json` directly into Postman:
1. Open Postman $\rightarrow$ Click **Import** $\rightarrow$ Select `blog-application-api/docs/postman_collection.json`.
2. Run the **Login User** request. The test script automatically saves the returned JWT token to the collection variable `token`.
3. All subsequent requests automatically use `Bearer {{token}}`.

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
