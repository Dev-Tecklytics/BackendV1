# IAAP Backend API Documentation

**Base URL:** `http://127.0.0.1:8000`  
**Version:** v1

---

## Table of Contents

1. [Authentication](#authentication)
2. [User Management](#user-management)
3. [Projects](#projects)
4. [Files](#files)
5. [Workflows](#workflows)
6. [Analysis](#analysis)
7. [Code Review](#code-review)
8. [Batch Processing](#batch-processing)
9. [Subscriptions](#subscriptions)
10. [API Keys](#api-keys)
11. [Export](#export)
12. [Compare](#compare)
13. [Health Check](#health-check)

---

## Authentication

### Register User

**POST** `/api/v1/auth/register`

Create a new user account with a 30-day trial subscription.

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "securePassword123",
  "full_name": "John Doe",
  "company_name": "Acme Corp"
}
```

**Response:** `200 OK`

```json
{
  "user_id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe"
}
```

**Errors:**

- `400` - Email already registered
- `500` - Database error

---

### Login

**POST** `/api/v1/auth/login`

Authenticate user and receive JWT access token.

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response:** `200 OK`

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "email": "user@example.com",
    "full_name": "John Doe",
    "user_id": "uuid"
  }
}
```

**Errors:**

- `401` - Invalid credentials

---

### Refresh Token

**POST** `/api/v1/auth/refresh-token`

Get a new access token using the current valid token.

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

### Logout

**POST** `/api/v1/auth/logout`

Logout the current user (client-side token removal).

**Response:** `204 No Content`

---

## User Management

### Get Current User Profile

**GET** `/api/v1/user/me`

Get the authenticated user's profile information.

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`

```json
{
  "user_id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe"
}
```

---

### Update User Profile

**PUT** `/api/v1/user/profile`

Update the authenticated user's profile.

**Headers:**

```
Authorization: Bearer <access_token>
```

**Query Parameters:**

- `full_name` (optional): New full name
- `company_name` (optional): New company name

**Response:** `200 OK`

```json
{
  "message": "Profile updated"
}
```

---

## Projects

### Create Project

**POST** `/api/v1/projects`

Create a new project for workflow analysis.

**Headers:**

```
Authorization: Bearer <access_token>
```

**Request Body:**

```json
{
  "name": "My RPA Project",
  "platform": "UiPath",
  "description": "Project description"
}
```

**Response:** `200 OK`

```json
{
  "project_id": "uuid",
  "name": "My RPA Project",
  "platform": "UiPath",
  "description": "Project description",
  "created_at": "2026-01-20T12:00:00Z"
}
```

---

### List All Projects

**GET** `/api/v1/projects`

Get all projects for the authenticated user.

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`

```json
[
  {
    "project_id": "uuid",
    "name": "My RPA Project",
    "platform": "UiPath",
    "description": "Project description",
    "created_at": "2026-01-20T12:00:00Z"
  }
]
```

---

### Get Single Project

**GET** `/api/v1/projects/{project_id}`

Get details of a specific project.

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`

```json
{
  "project_id": "uuid",
  "name": "My RPA Project",
  "platform": "UiPath",
  "description": "Project description",
  "created_at": "2026-01-20T12:00:00Z"
}
```

**Errors:**

- `404` - Project not found

---

### Update Project

**PATCH** `/api/v1/projects/{project_id}`

Update project details.

**Headers:**

```
Authorization: Bearer <access_token>
```

**Request Body:**

```json
{
  "name": "Updated Project Name",
  "description": "Updated description"
}
```

**Response:** `200 OK`

```json
{
  "project_id": "uuid",
  "name": "Updated Project Name",
  "platform": "UiPath",
  "description": "Updated description",
  "created_at": "2026-01-20T12:00:00Z"
}
```

**Errors:**

- `404` - Project not found

---

### Delete Project

**DELETE** `/api/v1/projects/{project_id}`

Delete a project.

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response:** `204 No Content`

**Errors:**

- `404` - Project not found

---

## Files

### Upload File

**POST** `/api/v1/files/upload`

Upload a workflow file to a project.

**Headers:**

```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Query Parameters:**

- `project_id` (required): UUID of the project

**Form Data:**

- `upload`: File to upload

**Response:** `200 OK`

```json
{
  "file_id": "uuid",
  "file_name": "workflow.xaml"
}
```

---

## Workflows

### Analyze Workflow

**POST** `/api/v1/workflows/analyze`

Analyze a workflow file for complexity metrics.

**Headers:**

```
Authorization: Bearer <access_token>
```

**Query Parameters:**

- `file_id` (required): UUID of the uploaded file
- `platform` (required): Platform name (e.g., "UiPath", "Automation Anywhere")

**Response:** `200 OK`

```json
{
  "complexity_score": 75,
  "complexity_level": "Medium",
  "nesting_depth": 3,
  "activity_count": 45,
  "variable_count": 12
}
```

**Errors:**

- `404` - File not found

---

## Analysis

### Analyze File

**POST** `/api/v1/analyze`

Perform analysis on a workflow file.

**Headers:**

```
Authorization: Bearer <access_token>
X-API-Key: <api_key>
```

**Query Parameters:**

- `file_name` (required): Name of the file to analyze

**Response:** `200 OK`

```json
{
  "analysis_id": "uuid",
  "status": "completed",
  "results": {}
}
```

---

### Analyze UiPath Workflow

**POST** `/api/v1/analyze/uipath`

Analyze a UiPath workflow file.

**Headers:**

```
Authorization: Bearer <access_token>
X-API-Key: <api_key>
Content-Type: multipart/form-data
```

**Form Data:**

- `file`: UiPath workflow file (.xaml)

**Response:** `200 OK`

```json
{
  "filename": "workflow.xaml",
  "status": "processing"
}
```

---

### Get Analysis Result

**GET** `/api/v1/analyze/{analysis_id}`

Get the result of a specific analysis.

**Response:** `200 OK`

```json
{
  "analysis_id": "uuid",
  "status": "completed"
}
```

---

## Code Review

### Review Workflow

**POST** `/api/v1/code-review`

Perform code review on a workflow.

**Headers:**

```
Authorization: Bearer <access_token>
```

**Query Parameters:**

- `workflow_id` (required): UUID of the workflow

**Response:** `200 OK`

```json
{
  "issues": [],
  "suggestions": [],
  "score": 85
}
```

**Errors:**

- `404` - Workflow not found

---

## Batch Processing

### Create Batch Job

**POST** `/api/v1/batch`

Create a batch processing job for multiple files.

**Headers:**

```
Authorization: Bearer <access_token>
```

**Query Parameters:**

- `project_id` (required): UUID of the project

**Response:** `200 OK`

```json
{
  "batch_id": "uuid"
}
```

---

## Subscriptions

### List Subscription Plans

**GET** `/api/v1/subscription/plans`

Get all available subscription plans.

**Response:** `200 OK`

```json
[
  {
    "plan_id": "uuid",
    "name": "Trial",
    "description": "30-day free trial",
    "price": 0.0,
    "billing_cycle": "monthly",
    "max_analyses_per_month": 10
  }
]
```

---

### Subscribe to Plan

**POST** `/api/v1/subscription/subscribe`

Subscribe to a specific plan.

**Headers:**

```
Authorization: Bearer <access_token>
```

**Query Parameters:**

- `plan_id` (required): UUID of the plan

**Response:** `200 OK`

```json
{
  "message": "Subscribed"
}
```

---

### Get Current Subscription

**GET** `/api/v1/subscription/current`

Get the user's current subscription.

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`

```json
{
  "subscription_id": "uuid",
  "plan_id": "uuid",
  "status": "trial",
  "start_date": "2026-01-20T12:00:00Z",
  "end_date": "2026-02-19T12:00:00Z"
}
```

---

### Upgrade Subscription

**PUT** `/api/v1/subscription/upgrade`

Upgrade the current subscription.

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`

```json
{
  "message": "Subscription upgraded"
}
```

---

### Cancel Subscription

**POST** `/api/v1/subscription/cancel`

Cancel the current subscription.

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`

```json
{
  "message": "Subscription cancelled"
}
```

---

### Get Subscription Usage

**GET** `/api/v1/subscription/usage`

Get usage statistics for the current subscription.

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`

```json
{
  "usage": "Usage details placeholder"
}
```

---

## API Keys

### Create API Key

**POST** `/api/v1/api_key`

Generate a new API key for programmatic access.

**Headers:**

```
Authorization: Bearer <access_token>
```

**Query Parameters:**

- `name` (optional): Name for the API key

**Response:** `200 OK`

```json
{
  "api_key": "iaap_1234567890abcdef",
  "name": "My API Key"
}
```

> **Important:** Save the API key securely. It will only be shown once.

---

### List API Keys

**GET** `/api/v1/api_key`

Get all API keys for the authenticated user.

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`

```json
[
  {
    "api_key_id": "uuid",
    "name": "My API Key",
    "key_prefix": "iaap_1234",
    "created_at": "2026-01-20T12:00:00Z",
    "is_active": true
  }
]
```

---

### Delete API Key

**DELETE** `/api/v1/api_key/{api_key_id}`

Deactivate an API key.

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response:** `204 No Content`

**Errors:**

- `404` - API key not found

---

### Rotate API Key

**PUT** `/api/v1/api_key/{api_key_id}/rotate`

Generate a new API key and invalidate the old one.

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`

```json
{
  "new_api_key": "iaap_newkey1234567890"
}
```

---

## Export

### Export to CSV

**GET** `/api/v1/export/csv`

Export workflow analysis results to CSV format.

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`

```csv
workflow_id,score,level
uuid,75,Medium
uuid,90,High
```

**Content-Type:** `text/csv`

---

## Compare

### Compare Workflows

**POST** `/api/v1/compare`

Compare workflow metrics.

**Query Parameters:**

- `activity_count` (required): Number of activities
- `mapped_activities` (required): Number of mapped activities

**Response:** `200 OK`

```json
{
  "mapping_percentage": 85.5,
  "unmapped_count": 7
}
```

---

## Health Check

### Health Check

**GET** `/health`

Check if the API is running.

**Response:** `200 OK`

```json
{
  "status": "ok"
}
```

---

## Authentication Methods

### Bearer Token (JWT)

Most endpoints require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <access_token>
```

### API Key

Some analysis endpoints support API key authentication:

```
X-API-Key: <api_key>
```

---

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message description"
}
```

### Common HTTP Status Codes

- `200` - Success
- `201` - Created
- `204` - No Content (successful deletion)
- `400` - Bad Request (validation error)
- `401` - Unauthorized (invalid or missing credentials)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `500` - Internal Server Error

---

## Rate Limiting

Rate limits are based on your subscription plan:

- **Trial**: 100 requests/hour
- **Basic**: 1000 requests/hour
- **Pro**: 5000 requests/hour
- **Enterprise**: Unlimited

---

## CORS Configuration

The API accepts requests from:

- `http://localhost:5173`
- `http://localhost:5174`
- `http://127.0.0.1:5173`
- `http://127.0.0.1:5174`

---

## Example Usage (JavaScript/TypeScript)

### Register and Login

```javascript
// Register
const registerResponse = await fetch(
  "http://127.0.0.1:8000/api/v1/auth/register",
  {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email: "user@example.com",
      password: "securePassword123",
      full_name: "John Doe",
    }),
  },
);

// Login
const loginResponse = await fetch("http://127.0.0.1:8000/api/v1/auth/login", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    email: "user@example.com",
    password: "securePassword123",
  }),
});

const { access_token } = await loginResponse.json();
```

### Create Project

```javascript
const projectResponse = await fetch("http://127.0.0.1:8000/api/v1/projects", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    Authorization: `Bearer ${access_token}`,
  },
  body: JSON.stringify({
    name: "My RPA Project",
    platform: "UiPath",
    description: "Project description",
  }),
});

const project = await projectResponse.json();
```

### Upload File

```javascript
const formData = new FormData();
formData.append("upload", fileInput.files[0]);

const uploadResponse = await fetch(
  `http://127.0.0.1:8000/api/v1/files/upload?project_id=${project.project_id}`,
  {
    method: "POST",
    headers: {
      Authorization: `Bearer ${access_token}`,
    },
    body: formData,
  },
);

const { file_id } = await uploadResponse.json();
```

### Analyze Workflow

```javascript
const analysisResponse = await fetch(
  `http://127.0.0.1:8000/api/v1/workflows/analyze?file_id=${file_id}&platform=UiPath`,
  {
    method: "POST",
    headers: {
      Authorization: `Bearer ${access_token}`,
    },
  },
);

const analysis = await analysisResponse.json();
console.log("Complexity Score:", analysis.complexity_score);
```

---

## Example Usage (Python)

```python
import requests

BASE_URL = "http://127.0.0.1:8000"

# Register
response = requests.post(f"{BASE_URL}/api/v1/auth/register", json={
    "email": "user@example.com",
    "password": "securePassword123",
    "full_name": "John Doe"
})

# Login
response = requests.post(f"{BASE_URL}/api/v1/auth/login", json={
    "email": "user@example.com",
    "password": "securePassword123"
})
token = response.json()["access_token"]

# Create Project
headers = {"Authorization": f"Bearer {token}"}
response = requests.post(f"{BASE_URL}/api/v1/projects",
    headers=headers,
    json={
        "name": "My RPA Project",
        "platform": "UiPath",
        "description": "Project description"
    }
)
project = response.json()

# Upload File
files = {"upload": open("workflow.xaml", "rb")}
response = requests.post(
    f"{BASE_URL}/api/v1/files/upload?project_id={project['project_id']}",
    headers=headers,
    files=files
)
file_data = response.json()

# Analyze Workflow
response = requests.post(
    f"{BASE_URL}/api/v1/workflows/analyze?file_id={file_data['file_id']}&platform=UiPath",
    headers=headers
)
analysis = response.json()
print(f"Complexity Score: {analysis['complexity_score']}")
```

---

## Support

For issues or questions, please contact the development team or refer to the project documentation.

**Last Updated:** 2026-01-20
