# BlogNest — RESTful Blog Application API

> **Objective**: Create a robust, production-grade RESTful API for a blog application that allows users to create, read, update, and delete blog posts, as well as manage comments with role-based access control, relational cascade integrity, and an interactive editorial web interface.

---

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Database Design & Schema](#database-design--schema)
3. [Process Flows](#process-flows)
   - [Authentication & JWT Issuance](#1-authentication--jwt-issuance-flow)
   - [Post Creation & Access Control](#2-post-creation--role-based-access-control-flow)
   - [Post Deletion & Automatic Comment Cascade Deletion](#3-post-deletion--cascade-deletion-flow)
4. [API Endpoints Overview](#api-endpoints-overview)
5. [User Manual & Step-by-Step API Guide](#user-manual--step-by-step-api-guide)
   - [Step 1: User Registration](#step-1-user-registration)
   - [Step 2: User Login & Token Acquisition](#step-2-user-login--token-acquisition)
   - [Step 3: Accessing Authenticated Profile](#step-3-accessing-authenticated-profile)
   - [Step 4: Creating a Blog Post](#step-4-creating-a-blog-post)
   - [Step 5: Reading Blog Posts (Paginated)](#step-5-reading-blog-posts-paginated)
   - [Step 6: Reading a Single Blog Post with Comments](#step-6-reading-a-single-blog-post-with-comments)
   - [Step 7: Adding a Comment to a Post](#step-7-adding-a-comment-to-a-post)
   - [Step 8: Reading Comments Filtered by Post ID](#step-8-reading-comments-filtered-by-post-id)
   - [Step 9: Updating Posts & Comments (Author Only)](#step-9-updating-posts--comments-author-only)
   - [Step 10: Deleting Posts & Verifying Cascade Deletion](#step-10-deleting-posts--verifying-cascade-deletion)
6. [Interactive Documentation (Swagger & Postman)](#interactive-documentation-swagger--postman)
7. [Frontend Web Application](#frontend-web-application)
8. [Environment Setup & Quickstart](#environment-setup--quickstart)
9. [Automated Testing Suite](#automated-testing-suite)
10. [Deliverables Verification](#deliverables-verification)

---

## System Architecture

BlogNest is engineered following a clean, modular multi-tier layered architecture, separating concerns between routing, schema validation, business logic repositories, and database persistence.

```mermaid
flowchart TD
    subgraph ClientLayer["1. Client & Presentation Layer"]
        BrowserUI["Web Frontend (HTML5 / Tailwind CSS / Vanilla JS)"]
        SwaggerUI["Swagger UI Playground (/docs)"]
        ExternalClients["External REST Clients (Postman, cURL, Mobile)"]
    end

    subgraph GatewayLayer["2. Routing & Middleware Layer"]
        ReverseProxy["WSGI Application (Flask Factory)"]
        CORSMiddleware["CORS Middleware (flask-cors)"]
        JWTMiddleware["JWT Authentication Guard (flask-jwt-extended)"]
        ErrorHandlers["Global Exception & Error Handlers (400, 401, 403, 404, 500)"]
    end

    subgraph ServiceLayer["3. Validation & Business Logic Layer"]
        AuthRoutes["Auth Controller (/register, /login, /me)"]
        PostRoutes["Posts Controller (/posts, /posts/:id)"]
        CommentRoutes["Comments Controller (/comments, /comments/:id)"]
        Validators["Input Validation Schemas (Email, Password, IDs, Payloads)"]
    end

    subgraph DataAccessLayer["4. Data Access Layer (Repositories)"]
        UserRepo["User Document Repository (Password Hashing, CRUD)"]
        PostRepo["Post Document Repository (Cascade Triggers, Feed Queries)"]
        CommentRepo["Comment Document Repository (Threaded Queries, Deletions)"]
    end

    subgraph StorageLayer["5. Database Storage Layer"]
        MongoDB[("MongoDB Database")]
        UsersColl[("users collection (Indexed)")]
        PostsColl[("posts collection (Indexed)")]
        CommentsColl[("comments collection (Indexed)")]
    end

    BrowserUI --> ReverseProxy
    SwaggerUI --> ReverseProxy
    ExternalClients --> ReverseProxy

    ReverseProxy --> CORSMiddleware
    CORSMiddleware --> JWTMiddleware
    JWTMiddleware --> ErrorHandlers

    ErrorHandlers --> AuthRoutes
    ErrorHandlers --> PostRoutes
    ErrorHandlers --> CommentRoutes

    AuthRoutes --> Validators
    PostRoutes --> Validators
    CommentRoutes --> Validators

    Validators --> UserRepo
    Validators --> PostRepo
    Validators --> CommentRepo

    UserRepo --> UsersColl
    PostRepo --> PostsColl
    CommentRepo --> CommentsColl

    UsersColl --- MongoDB
    PostsColl --- MongoDB
    CommentsColl --- MongoDB
```

---

## Database Design & Schema

BlogNest uses **MongoDB** as its document-oriented NoSQL database. Documents leverage BSON ObjectIds for primary keys with indexed foreign references establishing 1-to-many relationships.

```mermaid
erDiagram
    users ||--o{ posts : "author_id references users._id (1:N)"
    users ||--o{ comments : "author_id references users._id (1:N)"
    posts ||--o{ comments : "post_id references posts._id (1:N)"

    users {
        ObjectId _id PK "Unique Document Identifier"
        string username UK "Unique index, 3-30 alphanumeric"
        string email UK "Unique index, valid RFC email"
        string password "Salted & hashed with scrypt/werkzeug"
        datetime created_at "UTC timestamp"
        datetime updated_at "UTC timestamp"
    }

    posts {
        ObjectId _id PK "Unique Document Identifier"
        string title "1-255 characters"
        string content "Full blog post markdown or text"
        string author_id FK "Indexed reference to users._id"
        datetime created_at "Index: chronological sorting"
        datetime updated_at "UTC timestamp"
    }

    comments {
        ObjectId _id PK "Unique Document Identifier"
        string post_id FK "Indexed reference to posts._id"
        string content "Comment body"
        string author_id FK "Indexed reference to users._id"
        datetime created_at "Index: chronological sorting"
    }
```

### Collection Indexing & Performance Specifications
1. **`users` Collection**:
   - `{"username": 1}` with `unique=True`: Eliminates duplicate usernames with $O(1)$ lookups.
   - `{"email": 1}` with `unique=True`: Enforces unique email credentials.
2. **`posts` Collection**:
   - `{"author_id": 1}`: Accelerates author-specific queries.
   - `{"created_at": -1}`: Optimizes reverse-chronological feed retrieval without in-memory sorting.
3. **`comments` Collection**:
   - `{"post_id": 1}`: Fast retrieval of comment threads for any target post.
   - `{"author_id": 1}`: Enables tracking user activity and ownership enforcement.
   - `{"created_at": -1}`: Preserves chronological response ordering.

---

## Process Flows

### 1. Authentication & JWT Issuance Flow

```mermaid
sequenceDiagram
    autonumber
    actor Client as User / Client
    participant Auth as Auth Controller
    participant Val as Input Validator
    participant DB as MongoDB (users)
    participant JWT as JWT Manager

    Client->>Auth: POST /register {username, email, password}
    Auth->>Val: Validate username, email syntax, password >= 6 chars
    alt Invalid Payload
        Val-->>Auth: Validation Error
        Auth-->>Client: 400 Bad Request {error: "..."}
    else Valid Payload
        Val-->>Auth: Payload OK
        Auth->>DB: Check if username or email exists
        alt Duplicate User
            DB-->>Auth: Existing Record Found
            Auth-->>Client: 409 Conflict {error: "Username/Email already exists."}
        else New User
            Auth->>Auth: Hash password with werkzeug.security
            Auth->>DB: Insert User Document
            DB-->>Auth: Inserted ObjectId
            Auth->>JWT: Generate JWT Token (Identity = user._id)
            JWT-->>Auth: Access Token (Bearer)
            Auth-->>Client: 201 Created {user, access_token}
        end
    end
```

---

### 2. Post Creation & Role-Based Access Control Flow

```mermaid
sequenceDiagram
    autonumber
    actor Client as Authenticated Author
    participant Guard as JWT Middleware
    participant Controller as Posts Controller
    participant Val as Post Validator
    participant DB as MongoDB (posts)

    Client->>Guard: POST /posts (Header: Authorization: Bearer <token>)
    Guard->>Guard: Verify Token Signature & Expiry
    alt Missing / Invalid Token
        Guard-->>Client: 401 Unauthorized {error: "Unauthorized"}
    else Valid Token
        Guard->>Controller: Forward Request with user_id identity
        Controller->>Val: Validate {title: non-empty, content: non-empty}
        alt Validation Fails
            Val-->>Controller: Field missing
            Controller-->>Client: 400 Bad Request {error: "Title and content required."}
        else Validation Passes
            Controller->>DB: insert_one({title, content, author_id, created_at})
            DB-->>Controller: Generated Post Document
            Controller-->>Client: 201 Created {message: "Post created successfully.", post}
        end
    end
```

---

### 3. Post Deletion & Cascade Deletion Flow

```mermaid
sequenceDiagram
    autonumber
    actor Author as Post Author
    participant Controller as Posts Controller
    participant PostDB as MongoDB (posts)
    participant CommentDB as MongoDB (comments)

    Author->>Controller: DELETE /posts/:id (Bearer Token)
    Controller->>PostDB: find_by_id(post_id)
    alt Post Not Found
        PostDB-->>Controller: None
        Controller-->>Author: 404 Not Found {error: "Post not found."}
    else Post Exists
        PostDB-->>Controller: post_doc
        Controller->>Controller: Verify (post_doc.author_id == current_user_id)
        alt Not Author
            Controller-->>Author: 403 Forbidden {error: "Unauthorized: You can only delete your own posts."}
        else Is Author
            Controller->>PostDB: delete_one({_id: post_id})
            Controller->>CommentDB: delete_many({post_id: post_id}) (Cascade)
            CommentDB-->>Controller: deleted_count
            Controller-->>Author: 200 OK {message: "Post deleted successfully."}
        end
    end
```

---

## API Endpoints Overview

All endpoints support both standard root routes and `/api` prefixed routes.

### 1. Authentication Endpoints
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/register` | Register a new user account | No |
| `POST` | `/login` | Authenticate credentials and receive JWT | No |
| `GET` | `/me` | Fetch authenticated user profile | **Yes (Bearer JWT)** |

### 2. Blog Posts Endpoints
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/posts` | Read paginated posts (`?page=1&per_page=10&author_id=...`) | No |
| `GET` | `/posts/{id}` | Read single post with its populated comments | No |
| `POST` | `/posts` | Create a new blog post | **Yes (Bearer JWT)** |
| `PUT` | `/posts/{id}` | Update an existing post (Author only) | **Yes (Bearer JWT)** |
| `DELETE` | `/posts/{id}` | Delete post & cascade-delete all comments (Author only) | **Yes (Bearer JWT)** |

### 3. Comments Endpoints
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/comments` | Read comments (`?post_id=...&author_id=...&page=1`) | No |
| `GET` | `/comments/{id}` | Read single comment by ID | No |
| `POST` | `/comments` | Create comment on a post (`post_id`, `content`) | **Yes (Bearer JWT)** |
| `PUT` | `/comments/{id}` | Update comment (Author only) | **Yes (Bearer JWT)** |
| `DELETE` | `/comments/{id}` | Delete comment (Author only) | **Yes (Bearer JWT)** |
| `GET` | `/posts/{id}/comments` | Read all comments directly under a post | No |
| `POST` | `/posts/{id}/comments` | Add comment directly under a post | **Yes (Bearer JWT)** |

---

## User Manual & Step-by-Step API Guide

This section provides practical, copy-pasteable examples using `curl` and JSON payloads.

### Step 1: User Registration
Create a new user account.

```bash
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alex_writer",
    "email": "alex@example.com",
    "password": "Password123!"
  }'
```

**Expected Response (`201 Created`)**:
```json
{
  "message": "User registered successfully.",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "671b56a1e9447376c9682701",
    "username": "alex_writer",
    "email": "alex@example.com",
    "created_at": "2026-10-26T11:45:00+00:00",
    "updated_at": "2026-10-26T11:45:00+00:00"
  }
}
```

---

### Step 2: User Login & Token Acquisition
Authenticate to receive your JWT token.

```bash
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alex@example.com",
    "password": "Password123!"
  }'
```

**Expected Response (`200 OK`)**:
```json
{
  "message": "Login successful.",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "671b56a1e9447376c9682701",
    "username": "alex_writer",
    "email": "alex@example.com"
  }
}
```

---

### Step 3: Accessing Authenticated Profile
Verify your authentication status.

```bash
curl -X GET http://localhost:5000/me \
  -H "Authorization: Bearer <your_access_token>"
```

**Expected Response (`200 OK`)**:
```json
{
  "user": {
    "id": "671b56a1e9447376c9682701",
    "username": "alex_writer",
    "email": "alex@example.com",
    "created_at": "2026-10-26T11:45:00+00:00",
    "updated_at": "2026-10-26T11:45:00+00:00"
  }
}
```

---

### Step 4: Creating a Blog Post
Create a new article by providing a title and content.

```bash
curl -X POST http://localhost:5000/posts \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_access_token>" \
  -d '{
    "title": "Mastering Microservices Architecture with Python & MongoDB",
    "content": "Designing high-scale distributed systems requires modular boundaries, stateless authentication, and indexed document storage."
  }'
```

**Expected Response (`201 Created`)**:
```json
{
  "message": "Post created successfully.",
  "post": {
    "id": "671b56b3e9447376c9682702",
    "title": "Mastering Microservices Architecture with Python & MongoDB",
    "content": "Designing high-scale distributed systems requires modular boundaries, stateless authentication, and indexed document storage.",
    "author_id": "671b56a1e9447376c9682701",
    "author": "alex_writer",
    "comments_count": 0,
    "created_at": "2026-10-26T11:50:00+00:00",
    "updated_at": "2026-10-26T11:50:00+00:00"
  }
}
```

---

### Step 5: Reading Blog Posts (Paginated)
Fetch stories with server-side pagination and author filtering.

```bash
curl -X GET "http://localhost:5000/posts?page=1&per_page=10"
```

**Expected Response (`200 OK`)**:
```json
{
  "posts": [
    {
      "id": "671b56b3e9447376c9682702",
      "title": "Mastering Microservices Architecture with Python & MongoDB",
      "content": "Designing high-scale distributed systems...",
      "author_id": "671b56a1e9447376c9682701",
      "author": "alex_writer",
      "comments_count": 1,
      "created_at": "2026-10-26T11:50:00+00:00"
    }
  ],
  "page": 1,
  "per_page": 10,
  "total": 1,
  "pages": 1
}
```

---

### Step 6: Reading a Single Blog Post with Comments
Retrieve full post contents along with its populated comments thread.

```bash
curl -X GET http://localhost:5000/posts/671b56b3e9447376c9682702
```

**Expected Response (`200 OK`)**:
```json
{
  "post": {
    "id": "671b56b3e9447376c9682702",
    "title": "Mastering Microservices Architecture with Python & MongoDB",
    "content": "Designing high-scale distributed systems requires modular boundaries...",
    "author_id": "671b56a1e9447376c9682701",
    "author": "alex_writer",
    "comments": [
      {
        "id": "671b56c0e9447376c9682703",
        "post_id": "671b56b3e9447376c9682702",
        "content": "Incredible architectural insights!",
        "author_id": "671b56a1e9447376c9682799",
        "author": "reader_dev",
        "created_at": "2026-10-26T11:55:00+00:00"
      }
    ]
  }
}
```

---

### Step 7: Adding a Comment to a Post
Authenticated users can add responses to any post.

```bash
curl -X POST http://localhost:5000/comments \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_access_token>" \
  -d '{
    "post_id": "671b56b3e9447376c9682702",
    "content": "Incredible architectural insights! Very well articulated."
  }'
```

**Expected Response (`201 Created`)**:
```json
{
  "message": "Comment created successfully.",
  "comment": {
    "id": "671b56c0e9447376c9682703",
    "post_id": "671b56b3e9447376c9682702",
    "content": "Incredible architectural insights! Very well articulated.",
    "author_id": "671b56a1e9447376c9682701",
    "author": "alex_writer",
    "created_at": "2026-10-26T11:55:00+00:00"
  }
}
```

---

### Step 8: Reading Comments Filtered by Post ID
Query all comments associated with a specific blog post.

```bash
curl -X GET "http://localhost:5000/comments?post_id=671b56b3e9447376c9682702"
```

**Expected Response (`200 OK`)**:
```json
{
  "comments": [
    {
      "id": "671b56c0e9447376c9682703",
      "post_id": "671b56b3e9447376c9682702",
      "content": "Incredible architectural insights! Very well articulated.",
      "author_id": "671b56a1e9447376c9682701",
      "author": "alex_writer",
      "created_at": "2026-10-26T11:55:00+00:00"
    }
  ],
  "page": 1,
  "per_page": 20,
  "total": 1,
  "pages": 1
}
```

---

### Step 9: Updating Posts & Comments (Author Only)
Only authors are authorized to update their own content.

```bash
# Update Post
curl -X PUT http://localhost:5000/posts/671b56b3e9447376c9682702 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_access_token>" \
  -d '{
    "title": "Mastering Microservices Architecture with Python & MongoDB (Updated 2nd Edition)"
  }'

# Update Comment
curl -X PUT http://localhost:5000/comments/671b56c0e9447376c9682703 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_access_token>" \
  -d '{
    "content": "Updated comment: Truly exceptional guide!"
  }'
```

*Attempting to update another user's post returns `403 Forbidden`:*
```json
{
  "error": "Unauthorized: You can only update your own posts."
}
```

---

### Step 10: Deleting Posts & Verifying Cascade Deletion
When a post is deleted by its author, all associated comments are automatically cascade-deleted from MongoDB.

```bash
curl -X DELETE http://localhost:5000/posts/671b56b3e9447376c9682702 \
  -H "Authorization: Bearer <your_access_token>"
```

**Expected Response (`200 OK`)**:
```json
{
  "message": "Post deleted successfully."
}
```

Verifying that querying the deleted post returns `404 Not Found` and querying its comments returns an empty array:
```bash
curl -X GET http://localhost:5000/posts/671b56b3e9447376c9682702
# Returns: {"error": "Post not found."} (Status 404)

curl -X GET "http://localhost:5000/comments?post_id=671b56b3e9447376c9682702"
# Returns: {"comments": [], "total": 0} (Status 200)
```

---

## Interactive Documentation (Swagger & Postman)

### 1. Embedded Swagger UI
Start the server and open your browser:
👉 **[http://localhost:5000/docs](http://localhost:5000/docs)**
- Inspect schemas and parameters for all endpoints.
- Click **"Try it out"** $\rightarrow$ **"Execute"** to perform live requests directly in your browser.
- Raw OpenAPI 3.0 specification available at **[http://localhost:5000/swagger.json](http://localhost:5000/swagger.json)**.

### 2. Ready-to-Import Postman Collection
Import `blog-application-api/docs/postman_collection.json` into Postman:
1. Open Postman $\rightarrow$ Click **Import** $\rightarrow$ Choose `blog-application-api/docs/postman_collection.json`.
2. Run the **Login User** request. The test script automatically stores the returned JWT token into the `token` collection variable.
3. All subsequent requests automatically authenticate with `Bearer {{token}}`.

---

## Frontend Web Application

BlogNest includes a responsive, Medium-inspired web frontend built with pure Vanilla JavaScript and Tailwind CSS (zero external build tools required):
- **Live URL**: **[http://localhost:5000](http://localhost:5000)**
- **Story Feed**: Editorial layout with reading time estimates, author avatars, and timestamps.
- **Reading Canvas**: Dedicated distraction-free reading modal with claps counter and link sharing.
- **Interactive Comments**: Real-time response submissions with instant optimistic updates.
- **Story Writer**: Draft editor with live word count and reading time estimation.
- **Instant Search & Topic Filtering**: Filter by keyword or topics (`Technology`, `Python`, `MongoDB`, `Architecture`).

---

## Environment Setup & Quickstart

### 1. Prerequisites
- **Python 3.10+**
- **MongoDB** (Local instance at `mongodb://localhost:27017` or MongoDB Atlas cloud cluster)

### 2. Setup Virtual Environment
```powershell
# In PowerShell (Windows):
.\.venv\Scripts\Activate.ps1

# (Or in Linux/macOS):
source .venv/bin/activate
```

### 3. Configure Environment Variables
Create a `.env` file inside the `blog-application-api/` directory with the following configuration:

```env
MONGO_URI=mongodb://localhost:27017/blognest_db
MONGO_DBNAME=blognest_db
SECRET_KEY=super-secret-key-blognest-platform
JWT_SECRET_KEY=super-jwt-secret-key-32-chars-long-minimum!
PORT=5000
HOST=0.0.0.0
```

### 4. Initialize MongoDB Collections & Indexes
```powershell
cd blog-application-api
python init_db.py
```

### 5. Start the Application Server
```powershell
python run.py
```
- API Base URL: `http://localhost:5000`
- Web Frontend: `http://localhost:5000`
- Swagger UI Docs: `http://localhost:5000/docs`

---

## Automated Testing Suite

The test suite validates all endpoints, validation rules, authentication barriers, and cross-user permission boundaries using `pytest`:

```powershell
pytest
```

### Test Coverage Highlights
- `tests/test_auth.py`: Registration, duplicate username/email prevention (409), password length validation, login token generation.
- `tests/test_posts.py`: Post creation, paginated listing, single post retrieval with comments, author-only updates, and deletion.
- `tests/test_comments.py`: Comment creation on posts, post ID query filtering (`/comments?post_id=...`), author updates, and deletion.
- `tests/test_integration.py`: Complete multi-user lifecycle (User A creates post $\rightarrow$ User B comments $\rightarrow$ Unauthorized cross-user edit denial $\rightarrow$ Author updates post $\rightarrow$ Author deletes post $\rightarrow$ Automatic cascade comment deletion verified).

**Test Execution Result**: `12 passed in ~3s (0 warnings, 0 errors)`.

---

## Deliverables Verification

| Deliverable | Requirement | Implementation Status |
|---|---|---|
| **RESTful API** | Posts & Comments CRUD with validation & RBAC | ✅ Fully Implemented in `app/routes/` |
| **Database Schema** | MongoDB with indexes & cascade delete | ✅ Fully Implemented in `app/models/` & `init_db.py` |
| **Comprehensive Docs** | Swagger UI, Postman collection, User Manual | ✅ `/docs`, `swagger.json`, `postman_collection.json`, `README.md` |
| **Automated Tests** | Unit & Integration testing suite | ✅ 12 passed in `tests/` |
| **Web Frontend** | Modern, responsive editorial blogging UI | ✅ Available at `http://localhost:5000` |
| **Clean Codebase** | Modular architecture, single root documentation | ✅ Ready for Git repository submission |

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
