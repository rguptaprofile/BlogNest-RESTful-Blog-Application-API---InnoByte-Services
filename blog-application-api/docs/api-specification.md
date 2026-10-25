# BlogNest RESTful API Specification

**Project ID**: `SCR845NGFF`  
**Framework**: Python (Flask)  
**Database**: MongoDB (Document Store)  
**Authentication**: JSON Web Token (JWT Bearer)  
**Interactive UI**: `http://localhost:5000/docs` (Swagger UI)  
**OpenAPI Spec**: `http://localhost:5000/swagger.json`  
**Postman Collection**: `docs/postman_collection.json`  

---

## Base URLs
The API supports both direct routes (e.g., `/posts`, `/comments`, `/register`) and prefixed REST routes (e.g., `/api/posts`, `/api/comments`, `/api/auth/register`).

Header for Authenticated Endpoints:
```http
Authorization: Bearer <your_jwt_access_token>
Content-Type: application/json
```

---

## 1. Authentication Endpoints (Day 11-13)

### Register User
- **Method**: `POST`
- **Route**: `/register` or `/api/auth/register`
- **Auth Required**: No
- **Request Body**:
  ```json
  {
    "username": "johndoe",
    "email": "johndoe@example.com",
    "password": "Password123!"
  }
  ```
- **Validation Rules**:
  - `username`: 3-30 characters, alphanumeric & underscores only.
  - `email`: Valid email syntax.
  - `password`: Minimum 6 characters.
- **Success Response** (`201 Created`):
  ```json
  {
    "message": "User registered successfully.",
    "user": {
      "id": "671b56a1e9447376c9682701",
      "username": "johndoe",
      "email": "johndoe@example.com",
      "created_at": "2026-10-25T12:00:00+00:00",
      "updated_at": "2026-10-25T12:00:00+00:00"
    },
    "access_token": "eyJhbGciOiJIUzI1Ni..."
  }
  ```

### Login User
- **Method**: `POST`
- **Route**: `/login` or `/api/auth/login`
- **Auth Required**: No
- **Request Body**:
  ```json
  {
    "email": "johndoe@example.com",
    "password": "Password123!"
  }
  ```
- **Success Response** (`200 OK`):
  ```json
  {
    "message": "Login successful.",
    "user": {
      "id": "671b56a1e9447376c9682701",
      "username": "johndoe",
      "email": "johndoe@example.com"
    },
    "access_token": "eyJhbGciOiJIUzI1Ni..."
  }
  ```

### Current User Profile
- **Method**: `GET`
- **Route**: `/me` or `/api/auth/me`
- **Auth Required**: Yes
- **Success Response** (`200 OK`):
  ```json
  {
    "user": {
      "id": "671b56a1e9447376c9682701",
      "username": "johndoe",
      "email": "johndoe@example.com"
    }
  }
  ```

---

## 2. Blog Post Management Endpoints (Day 6-10)

### Read Posts (List)
- **Method**: `GET`
- **Route**: `/posts` or `/api/posts`
- **Query Params**:
  - `page` (int, default: 1)
  - `per_page` (int, default: 10, max: 100)
  - `author_id` (string ObjectId, optional filter)
- **Success Response** (`200 OK`):
  ```json
  {
    "posts": [
      {
        "id": "671b56b3e9447376c9682702",
        "title": "Mastering REST APIs with MongoDB",
        "content": "Full article markdown content...",
        "author_id": "671b56a1e9447376c9682701",
        "author": "johndoe",
        "comments_count": 2,
        "created_at": "2026-10-25T12:05:00+00:00",
        "updated_at": "2026-10-25T12:05:00+00:00"
      }
    ],
    "page": 1,
    "per_page": 10,
    "total": 1,
    "pages": 1
  }
  ```

### Read Single Post
- **Method**: `GET`
- **Route**: `/posts/{id}` or `/api/posts/{id}`
- **Success Response** (`200 OK`):
  ```json
  {
    "post": {
      "id": "671b56b3e9447376c9682702",
      "title": "Mastering REST APIs with MongoDB",
      "content": "Full article markdown content...",
      "author_id": "671b56a1e9447376c9682701",
      "author": "johndoe",
      "comments": [
        {
          "id": "671b56c0e9447376c9682703",
          "post_id": "671b56b3e9447376c9682702",
          "content": "Great explanation!",
          "author_id": "671b56a1e9447376c9682799",
          "author": "reader_user",
          "created_at": "2026-10-25T12:10:00+00:00"
        }
      ]
    }
  }
  ```

### Create Post
- **Method**: `POST`
- **Route**: `/posts` or `/api/posts`
- **Auth Required**: Yes
- **Request Body**:
  ```json
  {
    "title": "Mastering REST APIs with MongoDB",
    "content": "Full article markdown content..."
  }
  ```
- **Success Response** (`201 Created`)

### Update Post
- **Method**: `PUT`
- **Route**: `/posts/{id}` or `/api/posts/{id}`
- **Auth Required**: Yes (Author Only)
- **Request Body**:
  ```json
  {
    "title": "Updated Title",
    "content": "Updated Content"
  }
  ```
- **Success Response** (`200 OK`)

### Delete Post
- **Method**: `DELETE`
- **Route**: `/posts/{id}` or `/api/posts/{id}`
- **Auth Required**: Yes (Author Only)
- **Behavior**: Deletes post and automatically cascade-deletes all associated comments from MongoDB.
- **Success Response** (`200 OK`)

---

## 3. Comment Management Endpoints (Day 6-10)

### Read Comments (Filtered)
- **Method**: `GET`
- **Route**: `/comments` or `/api/comments`
- **Query Params**:
  - `post_id` (string, filter comments by target post)
  - `author_id` (string, filter comments by author)
  - `page` (int, default: 1)
  - `per_page` (int, default: 20)
- **Success Response** (`200 OK`)

### Read Single Comment
- **Method**: `GET`
- **Route**: `/comments/{id}` or `/api/comments/{id}`
- **Success Response** (`200 OK`)

### Create Comment
- **Method**: `POST`
- **Route**: `/comments` or `/api/comments`
- **Auth Required**: Yes
- **Request Body**:
  ```json
  {
    "post_id": "671b56b3e9447376c9682702",
    "content": "Insightful article, thank you!"
  }
  ```
- **Success Response** (`201 Created`)

### Update Comment
- **Method**: `PUT`
- **Route**: `/comments/{id}` or `/api/comments/{id}`
- **Auth Required**: Yes (Author Only)
- **Request Body**:
  ```json
  {
    "content": "Updated comment feedback."
  }
  ```
- **Success Response** (`200 OK`)

### Delete Comment
- **Method**: `DELETE`
- **Route**: `/comments/{id}` or `/api/comments/{id}`
- **Auth Required**: Yes (Author Only)
- **Success Response** (`200 OK`)

---

## 4. Standard Error Codes
| Status Code | Reason | Example Response |
|---|---|---|
| `400 Bad Request` | Missing field, invalid format, or malformed ID | `{"error": "Title and content are required."}` |
| `401 Unauthorized` | Missing, invalid, or expired JWT token | `{"error": "Invalid email or password."}` |
| `403 Forbidden` | Authenticated user is not the author of resource | `{"error": "Unauthorized: You can only update your own posts."}` |
| `404 Not Found` | Target post or comment does not exist | `{"error": "Post not found."}` |
| `409 Conflict` | Duplicate username or email registration | `{"error": "Username already exists."}` |
