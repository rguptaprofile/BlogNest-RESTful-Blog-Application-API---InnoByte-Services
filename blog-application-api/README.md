# BlogNest - RESTful Blog Application API

**Project ID**: `SCR845NGFF`  
**Duration**: 25 Days  
**Architecture**: Python / Flask RESTful API  
**Database**: MongoDB (via PyMongo)  
**Authentication**: JWT (JSON Web Tokens) with Role-Based Access Control  
**Documentation**: Swagger UI (`/docs`), OpenAPI 3.0 (`/swagger.json`), Postman Collection  

---

## Deliverables Checklist

- [x] **Fully functional RESTful API**: Complete CRUD operations for blog posts and comments.
- [x] **Database Schema & Setup Scripts**: MongoDB document collections, indexes, and automated setup (`init_db.py`).
- [x] **Comprehensive API Documentation**:
  - Interactive Swagger UI available at `/docs`
  - OpenAPI 3.0 specification in `docs/swagger.json`
  - Postman v2.1 collection in `docs/postman_collection.json`
  - Detailed Markdown specification in `docs/api-specification.md`
- [x] **Unit & Integration Test Cases**: Automated Pytest test suite covering all endpoints, permissions, and end-to-end integration flows.
- [x] **Repository Structure**: Clean, modular structure adhering to best practices.

---

## 25-Day Roadmap Implementation Mapping

| Phase | Description | Implemented Artifacts |
|---|---|---|
| **Day 1-2** | **Requirement Analysis** | Identified core models & endpoints; defined specification in [api-specification.md](docs/api-specification.md). |
| **Day 3-5** | **Database Design** | Designed MongoDB schema for `users`, `posts`, `comments` collections with unique indexes in [database-schema.md](docs/database-schema.md) & [init_db.py](init_db.py). |
| **Day 6-10** | **API Development** | Implemented post endpoints (`GET/POST /posts`, `GET/PUT/DELETE /posts/{id}`) and comment endpoints (`GET/POST /comments`, `GET/PUT/DELETE /comments/{id}`). |
| **Day 11-13** | **Authentication & Authorization** | Implemented JWT registration (`POST /register`), login (`POST /login`), profile (`GET /me`), and author-only access control. |
| **Day 14-16** | **Testing** | 12 automated unit & integration test cases in [tests/](tests/) with Pytest. |
| **Day 17-18** | **Documentation** | Interactive Swagger UI (`/docs`), [swagger.json](docs/swagger.json), and [postman_collection.json](docs/postman_collection.json). |
| **Day 19-21** | **Review & Refactor** | Modular schemas, helpers, error handlers, and performance optimizations. |
| **Day 22-25** | **Submission** | Final deliverables, documentation, and clean workspace ready for GitHub. |

---

## API Endpoints Overview

### 1. Authentication (`/register`, `/login`, `/me`)
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/register` (or `/api/auth/register`) | Register a new user | No |
| `POST` | `/login` (or `/api/auth/login`) | Authenticate user and receive JWT | No |
| `GET` | `/me` (or `/api/auth/me`) | Retrieve authenticated user profile | Yes |

### 2. Blog Posts (`/posts`, `/posts/{id}`)
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/posts` (or `/api/posts`) | Read paginated posts (supports `page`, `per_page`, `author_id`) | No |
| `GET` | `/posts/{id}` (or `/api/posts/{id}`) | Read single post and its comments | No |
| `POST` | `/posts` (or `/api/posts`) | Create new post | Yes |
| `PUT` | `/posts/{id}` (or `/api/posts/{id}`) | Update existing post (Author only) | Yes |
| `DELETE` | `/posts/{id}` (or `/api/posts/{id}`) | Delete post & cascade-delete its comments (Author only) | Yes |

### 3. Comments (`/comments`, `/comments/{id}`)
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/comments` (or `/api/comments`) | Read comments (supports `post_id`, `author_id`, `page`) | No |
| `GET` | `/comments/{id}` (or `/api/comments/{id}`) | Read single comment | No |
| `POST` | `/comments` (or `/api/comments`) | Create new comment on post (`post_id`, `content`) | Yes |
| `PUT` | `/comments/{id}` (or `/api/comments/{id}`) | Update comment (Author only) | Yes |
| `DELETE` | `/comments/{id}` (or `/api/comments/{id}`) | Delete comment (Author only) | Yes |
| `GET` | `/posts/{id}/comments` | Read all comments directly under a post | No |
| `POST` | `/posts/{id}/comments` | Add comment directly under a post | Yes |

---

## Quickstart Guide

### 1. Prerequisites
- Python 3.10+
- MongoDB instance (local `mongodb://localhost:27017` or MongoDB Atlas cloud cluster)

### 2. Environment Setup
```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Create environment configuration
Copy-Item blog-application-api\.env.example blog-application-api\.env
```

Set your MongoDB connection in `.env`:
```env
MONGO_URI=mongodb://localhost:27017/blognest_db
MONGO_DBNAME=blognest_db
```

### 3. Initialize MongoDB Indexes
```powershell
cd blog-application-api
python init_db.py
```

### 4. Run the API Server
```powershell
python run.py
```
- API Base: `http://localhost:5000`
- **Interactive Swagger Documentation**: `http://localhost:5000/docs`
- OpenAPI Specification: `http://localhost:5000/swagger.json`

### 5. Run Automated Tests
```powershell
pytest
```
Expected output: **12 passed**.

---

## Postman Collection Usage
Import [docs/postman_collection.json](docs/postman_collection.json) directly into Postman:
1. Open Postman $\rightarrow$ Click **Import** $\rightarrow$ Choose `docs/postman_collection.json`.
2. Execute **Login User** request. The test script automatically captures and stores the JWT access token in the `token` collection variable.
3. All subsequent authenticated requests automatically include the `Bearer {{token}}` header.
