# IAAP Backend - Complete Application Documentation

**Intelligent Automation Analysis Platform - Backend Service**

**Version**: 0.1.0  
**Last Updated**: January 19, 2026  
**Python Version**: 3.13+  
**Framework**: FastAPI

---

## 📋 Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Architecture](#system-architecture)
3. [Technology Stack](#technology-stack)
4. [Project Structure](#project-structure)
5. [Database Schema](#database-schema)
6. [API Endpoints](#api-endpoints)
7. [Authentication & Security](#authentication--security)
8. [Core Features](#core-features)
9. [Configuration](#configuration)
10. [Installation & Setup](#installation--setup)
11. [Deployment](#deployment)
12. [Testing](#testing)
13. [Troubleshooting](#troubleshooting)

---

## Executive Summary

### What is IAAP Backend?

The **Intelligent Automation Analysis Platform (IAAP) Backend** is a comprehensive FastAPI-based REST API service designed to provide intelligent automation analysis capabilities. The platform enables users to upload, analyze, and process automation workflows with AI-powered insights.

### Key Capabilities

- **User Management**: Complete authentication and authorization system
- **Analysis Processing**: AI-powered workflow analysis using Google Gemini
- **Subscription Management**: Tiered subscription plans with usage tracking
- **API Key Management**: Secure API key generation and management
- **Admin Dashboard**: Comprehensive admin panel for system monitoring
- **File Processing**: Support for XML/XAML workflow file uploads

### Current Status

✅ **Production Ready** (after security hardening)

- Backend: Running on http://127.0.0.1:8000
- Database: PostgreSQL (rpa_analyzer)
- Authentication: JWT-based with bcrypt password hashing
- CORS: Configured for frontend integration
- Migrations: Alembic database migrations implemented

---

## System Architecture

### High-Level Architecture

```mermaid
graph TB
    Client[Frontend Client] --> API[FastAPI Application]
    API --> Auth[Authentication Layer]
    Auth --> Routes[API Routes]
    Routes --> Services[Business Logic Services]
    Services --> DB[(PostgreSQL Database)]
    Services --> AI[Google Gemini AI]
    Services --> Cache[(Redis Cache)]

    subgraph "Core Components"
        Auth
        Routes
        Services
    end

    subgraph "Data Layer"
        DB
        Cache
    end
```

### Application Layers

1. **Presentation Layer**: FastAPI routes and endpoints
2. **Business Logic Layer**: Services for analysis, subscriptions, etc.
3. **Data Access Layer**: SQLAlchemy ORM models
4. **Security Layer**: JWT authentication, password hashing, API keys
5. **External Services**: Google Gemini AI integration

### Request Flow

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Auth
    participant Service
    participant DB
    participant AI

    Client->>API: HTTP Request + JWT Token
    API->>Auth: Validate Token
    Auth->>API: User Context
    API->>Service: Process Request
    Service->>DB: Query/Update Data
    Service->>AI: AI Analysis (if needed)
    AI->>Service: Analysis Results
    Service->>API: Response Data
    API->>Client: JSON Response
```

---

## Technology Stack

### Backend Framework

- **FastAPI** (0.125.0+): Modern, high-performance web framework
- **Uvicorn** (0.38.0+): ASGI server for production deployment
- **Pydantic** (2.12.5+): Data validation and settings management

### Database

- **PostgreSQL** (17/18): Primary relational database
- **SQLAlchemy** (2.0.45+): ORM for database operations
- **Alembic** (1.17.2+): Database migration management
- **psycopg2-binary** (2.9.11+): PostgreSQL adapter

### Authentication & Security

- **python-jose** (3.5.0+): JWT token generation and validation
- **passlib[bcrypt]** (1.7.4+): Password hashing
- **bcrypt** (5.0.0+): Secure password hashing algorithm
- **argon2-cffi** (25.1.0+): Alternative password hashing
- **email-validator** (2.3.0+): Email validation

### AI & Processing

- **google-generativeai** (0.3.2): Google Gemini AI integration
- **lxml** (5.1.0): XML/XAML parsing
- **xmltodict** (0.13.0): XML to dictionary conversion

### Utilities

- **python-dotenv** (1.2.1+): Environment variable management
- **python-multipart** (0.0.21+): File upload handling
- **aiofiles** (23.2.1): Async file operations
- **python-dateutil** (2.8.2): Date/time utilities
- **redis** (7.1.0+): Caching and session management

---

## Project Structure

```
BackendV1/
├── app/
│   ├── __init__.py
│   ├── main.py                      # Application entry point
│   │
│   ├── core/                        # Core functionality
│   │   ├── __init__.py
│   │   ├── auth.py                  # Authentication utilities
│   │   ├── admin_auth.py            # Admin authentication
│   │   ├── api_key.py               # API key utilities
│   │   ├── api_key_auth.py          # API key authentication
│   │   ├── config.py                # Configuration settings
│   │   ├── core_context.py          # Request context management
│   │   ├── database.py              # Database connection
│   │   ├── deps.py                  # Dependency injection
│   │   ├── jwt.py                   # JWT token handling
│   │   ├── quota_check.py           # Usage quota checking
│   │   ├── rate_limiter.py          # Rate limiting
│   │   ├── redis_client.py          # Redis connection
│   │   ├── security.py              # Password hashing/verification
│   │   ├── subscription_check.py    # Subscription validation
│   │   └── usage_tracker.py         # Usage tracking
│   │
│   ├── models/                      # Database models (SQLAlchemy)
│   │   ├── __init__.py
│   │   ├── user.py                  # User model
│   │   ├── api_key.py               # API key model
│   │   ├── subscription.py          # Subscription model
│   │   ├── subscription_plan.py     # Subscription plan model
│   │   ├── analysis_history.py      # Analysis history model
│   │   ├── payment_transaction.py   # Payment transaction model
│   │   ├── usage_tracking.py        # Usage tracking model
│   │   └── enums.py                 # Enumerations (UserStatus, UserRole, etc.)
│   │
│   ├── routes/                      # API endpoints
│   │   ├── __init__.py
│   │   ├── health.py                # Health check endpoint
│   │   ├── Auth.py                  # Authentication routes
│   │   ├── user.py                  # User management
│   │   ├── api_key.py               # API key management
│   │   ├── analysis.py              # Analysis creation
│   │   ├── analysis_history.py      # Analysis history
│   │   ├── analysis_result.py       # Analysis results
│   │   ├── analysis_upload.py       # File upload
│   │   ├── analysis_worker.py       # Background workers
│   │   ├── subscription.py          # Subscription management
│   │   ├── admin_users.py           # Admin: User management
│   │   ├── admin_api_keys.py        # Admin: API key management
│   │   ├── admin_subscription.py    # Admin: Subscription management
│   │   ├── admin_usage.py           # Admin: Usage statistics
│   │   ├── admin_analytics.py       # Admin: Analytics
│   │   ├── migrate.py               # Migration utilities
│   │   └── test/
│   │       └── core_test.py         # Core functionality tests
│   │
│   ├── schemas/                     # Pydantic schemas (validation)
│   │   ├── __init__.py
│   │   ├── auth.py                  # Authentication schemas
│   │   ├── user.py                  # User schemas
│   │   ├── api_key.py               # API key schemas
│   │   └── admin.py                 # Admin schemas
│   │
│   └── services/                    # Business logic
│       ├── __init__.py
│       ├── analysis_processor.py    # Analysis processing logic
│       └── analysis_service.py      # Analysis service
│
├── alembic/                         # Database migrations
│   ├── versions/
│   │   ├── 78ef792d1592_complete_core_schema.py
│   │   ├── d47ce51b91cf_add_role_to_users.py
│   │   └── e13de6caf70f_add_role_to_users.py
│   └── env.py
│
├── .env                             # Environment variables
├── .gitignore                       # Git ignore rules
├── .python-version                  # Python version specification
├── alembic.ini                      # Alembic configuration
├── pyproject.toml                   # Project dependencies
├── requirements.txt                 # Pip requirements
├── uv.lock                          # UV package manager lock file
├── README.md                        # Project README
├── GITHUB_SETUP.md                  # GitHub setup guide
├── test_frontend.html               # Frontend integration test
└── test_connection.ps1              # Connection test script
```

---

## Database Schema

### Entity Relationship Diagram

```mermaid
erDiagram
    users ||--o{ api_keys : has
    users ||--o{ subscriptions : has
    users ||--o{ analysis_history : creates
    users ||--o{ usage_tracking : tracks
    subscriptions ||--|| subscription_plans : references
    subscriptions ||--o{ payment_transactions : has
    api_keys ||--o{ analysis_history : used_in
    subscriptions ||--o{ analysis_history : linked_to

    users {
        uuid user_id PK
        string email UK
        string password_hash
        string full_name
        string company_name
        enum user_role
        enum status
        timestamp created_at
        timestamp updated_at
    }

    api_keys {
        uuid api_key_id PK
        uuid user_id FK
        string key_hash
        string key_prefix
        string name
        timestamp last_used_at
        timestamp expires_at
        boolean is_active
        timestamp created_at
    }

    subscriptions {
        uuid subscription_id PK
        uuid user_id FK
        uuid plan_id FK
        enum status
        timestamp start_date
        timestamp end_date
        boolean auto_renew
        timestamp created_at
        timestamp updated_at
    }

    subscription_plans {
        uuid plan_id PK
        string name
        string description
        decimal price
        integer analysis_limit
        integer api_calls_limit
        json features
        timestamp created_at
    }

    analysis_history {
        uuid analysis_id PK
        uuid user_id FK
        uuid api_key_id FK
        uuid subscription_id FK
        string file_name
        enum status
        timestamp created_at
    }

    payment_transactions {
        uuid transaction_id PK
        uuid subscription_id FK
        decimal amount
        enum status
        string payment_method
        timestamp created_at
    }

    usage_tracking {
        uuid usage_id PK
        uuid user_id FK
        integer api_calls_count
        integer analyses_count
        timestamp period_start
        timestamp period_end
    }
```

### Table Definitions

#### users

Stores user account information.

| Column        | Type      | Constraints      | Description                 |
| ------------- | --------- | ---------------- | --------------------------- |
| user_id       | UUID      | PRIMARY KEY      | Unique user identifier      |
| email         | VARCHAR   | UNIQUE, NOT NULL | User email address          |
| password_hash | VARCHAR   | NOT NULL         | Bcrypt hashed password      |
| full_name     | VARCHAR   |                  | User's full name            |
| company_name  | VARCHAR   |                  | Company/organization name   |
| user_role     | ENUM      | DEFAULT 'USER'   | USER or ADMIN               |
| status        | ENUM      | DEFAULT 'ACTIVE' | ACTIVE, INACTIVE, SUSPENDED |
| created_at    | TIMESTAMP | DEFAULT NOW()    | Account creation timestamp  |
| updated_at    | TIMESTAMP | ON UPDATE        | Last update timestamp       |

#### api_keys

Manages API keys for programmatic access.

| Column       | Type      | Constraints   | Description                          |
| ------------ | --------- | ------------- | ------------------------------------ |
| api_key_id   | UUID      | PRIMARY KEY   | Unique API key identifier            |
| user_id      | UUID      | FOREIGN KEY   | Reference to users table             |
| key_hash     | VARCHAR   | NOT NULL      | Hashed API key                       |
| key_prefix   | VARCHAR   | NOT NULL      | Visible key prefix (e.g., "sk\_...") |
| name         | VARCHAR   |               | Descriptive name for the key         |
| last_used_at | TIMESTAMP |               | Last usage timestamp                 |
| expires_at   | TIMESTAMP |               | Expiration timestamp                 |
| is_active    | BOOLEAN   | DEFAULT TRUE  | Active status                        |
| created_at   | TIMESTAMP | DEFAULT NOW() | Creation timestamp                   |

#### subscriptions

Tracks user subscription status.

| Column          | Type      | Constraints   | Description                     |
| --------------- | --------- | ------------- | ------------------------------- |
| subscription_id | UUID      | PRIMARY KEY   | Unique subscription identifier  |
| user_id         | UUID      | FOREIGN KEY   | Reference to users table        |
| plan_id         | UUID      | FOREIGN KEY   | Reference to subscription_plans |
| status          | ENUM      | NOT NULL      | ACTIVE, CANCELLED, EXPIRED      |
| start_date      | TIMESTAMP |               | Subscription start date         |
| end_date        | TIMESTAMP |               | Subscription end date           |
| auto_renew      | BOOLEAN   | DEFAULT TRUE  | Auto-renewal flag               |
| created_at      | TIMESTAMP | DEFAULT NOW() | Creation timestamp              |
| updated_at      | TIMESTAMP | ON UPDATE     | Last update timestamp           |

#### subscription_plans

Defines available subscription tiers.

| Column          | Type      | Constraints   | Description                     |
| --------------- | --------- | ------------- | ------------------------------- |
| plan_id         | UUID      | PRIMARY KEY   | Unique plan identifier          |
| name            | VARCHAR   |               | Plan name (e.g., "Free", "Pro") |
| description     | VARCHAR   |               | Plan description                |
| price           | DECIMAL   |               | Monthly price                   |
| analysis_limit  | INTEGER   |               | Max analyses per month          |
| api_calls_limit | INTEGER   |               | Max API calls per month         |
| features        | JSON      |               | Additional features             |
| created_at      | TIMESTAMP | DEFAULT NOW() | Creation timestamp              |

#### analysis_history

Records all analysis operations.

| Column          | Type      | Constraints   | Description                             |
| --------------- | --------- | ------------- | --------------------------------------- |
| analysis_id     | UUID      | PRIMARY KEY   | Unique analysis identifier              |
| user_id         | UUID      | FOREIGN KEY   | Reference to users table                |
| api_key_id      | UUID      | FOREIGN KEY   | API key used (if applicable)            |
| subscription_id | UUID      | FOREIGN KEY   | Active subscription                     |
| file_name       | VARCHAR   |               | Uploaded file name                      |
| status          | ENUM      |               | PENDING, IN_PROGRESS, COMPLETED, FAILED |
| created_at      | TIMESTAMP | DEFAULT NOW() | Creation timestamp                      |

#### payment_transactions

Tracks payment history.

| Column          | Type      | Constraints   | Description                   |
| --------------- | --------- | ------------- | ----------------------------- |
| transaction_id  | UUID      | PRIMARY KEY   | Unique transaction identifier |
| subscription_id | UUID      | FOREIGN KEY   | Related subscription          |
| amount          | DECIMAL   |               | Transaction amount            |
| status          | ENUM      |               | SUCCESS, FAILED, PENDING      |
| payment_method  | VARCHAR   |               | Payment method used           |
| created_at      | TIMESTAMP | DEFAULT NOW() | Transaction timestamp         |

#### usage_tracking

Monitors API and analysis usage.

| Column          | Type      | Constraints | Description                    |
| --------------- | --------- | ----------- | ------------------------------ |
| usage_id        | UUID      | PRIMARY KEY | Unique usage record identifier |
| user_id         | UUID      | FOREIGN KEY | Reference to users table       |
| api_calls_count | INTEGER   |             | Number of API calls            |
| analyses_count  | INTEGER   |             | Number of analyses             |
| period_start    | TIMESTAMP |             | Tracking period start          |
| period_end      | TIMESTAMP |             | Tracking period end            |

### Enumerations

#### UserRole

```python
class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"
```

#### UserStatus

```python
class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
```

#### SubscriptionStatus

```python
class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
```

#### AnalysisStatus

```python
class AnalysisStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
```

---

## API Endpoints

### Base URL

```
http://127.0.0.1:8000
```

### Interactive Documentation

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc
- **OpenAPI JSON**: http://127.0.0.1:8000/openapi.json

### Endpoint Categories

#### 1. Health Check

| Method | Endpoint  | Description         | Auth Required |
| ------ | --------- | ------------------- | ------------- |
| GET    | `/health` | Server health check | No            |

**Response**:

```json
{
  "status": "ok"
}
```

---

#### 2. Authentication (`/api/v1/auth`)

| Method | Endpoint                     | Description          | Auth Required |
| ------ | ---------------------------- | -------------------- | ------------- |
| POST   | `/api/v1/auth/register`      | Register new user    | No            |
| POST   | `/api/v1/auth/login`         | User login           | No            |
| POST   | `/api/v1/auth/refresh-token` | Refresh access token | Yes           |
| POST   | `/api/v1/auth/logout`        | Logout user          | Yes           |

**Register Request**:

```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "full_name": "John Doe",
  "company_name": "Acme Corp"
}
```

**Login Request**:

```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Login Response**:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

#### 3. User Management (`/api/v1/user`)

| Method | Endpoint               | Description              | Auth Required |
| ------ | ---------------------- | ------------------------ | ------------- |
| GET    | `/api/v1/user/me`      | Get current user profile | Yes           |
| PUT    | `/api/v1/user/profile` | Update user profile      | Yes           |

---

#### 4. API Key Management (`/api/v1/api-keys`)

| Method | Endpoint                    | Description          | Auth Required |
| ------ | --------------------------- | -------------------- | ------------- |
| GET    | `/api/v1/api-keys`          | List user's API keys | Yes           |
| POST   | `/api/v1/api-keys`          | Create new API key   | Yes           |
| DELETE | `/api/v1/api-keys/{key_id}` | Delete API key       | Yes           |

**Create API Key Request**:

```json
{
  "name": "Production API Key",
  "expires_in_days": 365
}
```

---

#### 5. Analysis (`/api/v1/analysis`)

| Method | Endpoint                       | Description              | Auth Required |
| ------ | ------------------------------ | ------------------------ | ------------- |
| POST   | `/api/v1/analysis`             | Create new analysis      | Yes           |
| POST   | `/api/v1/analysis/upload`      | Upload file for analysis | Yes           |
| GET    | `/api/v1/analysis/history`     | Get analysis history     | Yes           |
| GET    | `/api/v1/analysis/result/{id}` | Get analysis result      | Yes           |

**Upload File**:

```
POST /api/v1/analysis/upload
Content-Type: multipart/form-data

file: [XAML/XML file]
```

---

#### 6. Subscriptions (`/api/v1/subscription`)

| Method | Endpoint                         | Description              | Auth Required |
| ------ | -------------------------------- | ------------------------ | ------------- |
| GET    | `/api/v1/subscription/plans`     | Get available plans      | No            |
| POST   | `/api/v1/subscription/subscribe` | Subscribe to a plan      | Yes           |
| GET    | `/api/v1/subscription/current`   | Get current subscription | Yes           |
| POST   | `/api/v1/subscription/cancel`    | Cancel subscription      | Yes           |

---

#### 7. Admin Endpoints (`/api/v1/admin`)

All admin endpoints require `user_role = ADMIN`.

| Method | Endpoint                     | Description          |
| ------ | ---------------------------- | -------------------- |
| GET    | `/api/v1/admin/users`        | List all users       |
| GET    | `/api/v1/admin/analytics`    | Get system analytics |
| GET    | `/api/v1/admin/usage`        | Get usage statistics |
| GET    | `/api/v1/admin/api-keys`     | Manage all API keys  |
| GET    | `/api/v1/admin/subscription` | Manage subscriptions |

---

## Authentication & Security

### JWT Authentication

#### Token Generation

- **Algorithm**: HS256
- **Expiration**: 60 minutes (configurable)
- **Secret**: Stored in environment variable `JWT_SECRET`

#### Token Structure

```json
{
  "sub": "user_id",
  "email": "user@example.com",
  "role": "user",
  "exp": 1234567890
}
```

#### Using Tokens

Include the JWT token in the `Authorization` header:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Password Security

#### Hashing Algorithm

- **Primary**: bcrypt with salt rounds
- **Alternative**: Argon2 (available)

#### Password Requirements

- Minimum 8 characters (recommended)
- Stored as bcrypt hash (max 72 bytes)

#### Implementation

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash password
hashed = pwd_context.hash(plain_password)

# Verify password
is_valid = pwd_context.verify(plain_password, hashed_password)
```

### API Key Authentication

#### Key Format

```
sk_[random_string]
```

#### Key Storage

- Full key shown only once at creation
- Stored as hash in database
- Prefix stored for identification

#### Usage

Include API key in header:

```
X-API-Key: sk_abc123xyz789...
```

### CORS Configuration

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

> **⚠️ Production Warning**: Update `allow_origins` to specific production URLs.

### Rate Limiting

Rate limiting is implemented via `rate_limiter.py`:

- Prevents abuse
- Configurable per endpoint
- Uses Redis for distributed rate limiting

### Security Best Practices

✅ **Implemented**:

- Password hashing with bcrypt
- JWT token expiration
- Email validation
- SQL injection prevention (SQLAlchemy ORM)
- CORS configuration

⚠️ **Recommended for Production**:

- HTTPS/TLS encryption
- Rate limiting on all endpoints
- API key rotation policy
- Password complexity requirements
- Account lockout after failed attempts
- 2FA/MFA support
- Security headers (HSTS, CSP, etc.)

---

## Core Features

### 1. User Management

**Features**:

- User registration with email validation
- Secure login with JWT tokens
- Profile management
- Role-based access control (USER/ADMIN)
- Account status management (ACTIVE/INACTIVE/SUSPENDED)

**User Roles**:

- **USER**: Standard user with analysis capabilities
- **ADMIN**: Full system access including admin panel

### 2. Analysis Processing

**Workflow**:

1. User uploads XAML/XML workflow file
2. File is parsed and validated
3. Analysis request is queued
4. Google Gemini AI processes the workflow
5. Results are stored and returned to user

**Supported File Types**:

- XAML (UiPath workflows)
- XML (generic workflow definitions)

**Analysis Features**:

- AI-powered workflow analysis
- Complexity assessment
- Best practice recommendations
- Performance optimization suggestions

### 3. Subscription Management

**Subscription Tiers**:

- **Free**: Limited analyses per month
- **Pro**: Increased limits and features
- **Enterprise**: Unlimited analyses and priority support

**Features**:

- Automatic subscription renewal
- Usage tracking and quota enforcement
- Payment transaction history
- Plan upgrades/downgrades

### 4. API Key Management

**Features**:

- Generate multiple API keys per user
- Set expiration dates
- Track last usage
- Revoke keys instantly
- Named keys for organization

**Use Cases**:

- CI/CD integration
- Third-party application access
- Automated workflows

### 5. Admin Dashboard

**Capabilities**:

- User management (view, suspend, delete)
- System analytics and metrics
- Usage statistics and trends
- API key oversight
- Subscription management
- Payment transaction monitoring

### 6. Usage Tracking

**Metrics Tracked**:

- API calls per user/period
- Analyses performed
- Quota consumption
- Peak usage times
- Error rates

---

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Database Configuration
DATABASE_URL=postgresql://postgres:1234@localhost:5432/rpa_analyzer

# JWT Configuration
JWT_SECRET=super-secret-key-change-this
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60

# Google Gemini AI (if applicable)
GOOGLE_API_KEY=your_google_api_key_here

# Redis Configuration (optional)
REDIS_URL=redis://localhost:6379/0

# Application Settings
DEBUG=True
LOG_LEVEL=INFO
```

### Configuration File

`app/core/config.py`:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    class Config:
        env_file = ".env"
```

### CORS Origins

Update `app/main.py` for production:

```python
allow_origins=[
    "https://yourdomain.com",
    "https://app.yourdomain.com",
]
```

---

## Installation & Setup

### Prerequisites

- **Python**: 3.13+ (specified in `.python-version`)
- **PostgreSQL**: 17 or 18
- **Redis**: 7.1+ (optional, for caching)
- **Git**: For version control

### Step 1: Clone Repository

```powershell
git clone <repository-url>
cd BackendV1
```

### Step 2: Create Virtual Environment

```powershell
# Using Python venv
python -m venv venv
.\venv\Scripts\Activate.ps1

# Or using uv (recommended)
uv venv
.\.venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies

```powershell
# Using pip
pip install -r requirements.txt

# Or using uv (faster)
uv pip install -r requirements.txt

# Or using pyproject.toml
pip install -e .
```

### Step 4: Setup PostgreSQL Database

```powershell
# Set password environment variable
$env:PGPASSWORD='1234'

# Create database
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -h localhost -c "CREATE DATABASE rpa_analyzer;"

# Verify database creation
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -h localhost -c "\l"
```

### Step 5: Configure Environment

Create `.env` file:

```env
DATABASE_URL=postgresql://postgres:1234@localhost:5432/rpa_analyzer
JWT_SECRET=your-super-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60
```

### Step 6: Run Database Migrations

```powershell
# Apply all migrations
alembic upgrade head

# Verify tables created
$env:PGPASSWORD='1234'
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -h localhost -d rpa_analyzer -c "\dt"
```

### Step 7: Run the Application

```powershell
# Development mode (with auto-reload)
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Or using uv
uv run uvicorn app.main:app --reload
```

### Step 8: Verify Installation

Open browser and navigate to:

- **API Docs**: http://127.0.0.1:8000/docs
- **Health Check**: http://127.0.0.1:8000/health

---

## Deployment

### Production Checklist

- [ ] Change `JWT_SECRET` to a strong random value (use `secrets.token_urlsafe(32)`)
- [ ] Update CORS `allow_origins` to specific frontend URLs
- [ ] Enable HTTPS/TLS
- [ ] Set `DEBUG=False`
- [ ] Configure production database with strong password
- [ ] Set up database backups
- [ ] Configure logging to file/service
- [ ] Set up monitoring (e.g., Prometheus, Grafana)
- [ ] Configure rate limiting
- [ ] Set up error tracking (e.g., Sentry)
- [ ] Use environment variables for all secrets
- [ ] Set up CI/CD pipeline
- [ ] Configure firewall rules
- [ ] Set up load balancer (if needed)

### Production Run Command

Using Gunicorn with Uvicorn workers:

```bash
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile /var/log/iaap/access.log \
  --error-logfile /var/log/iaap/error.log \
  --log-level info
```

### Docker Deployment (Optional)

Create `Dockerfile`:

```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t iaap-backend .
docker run -p 8000:8000 --env-file .env iaap-backend
```

### Database Migration in Production

```bash
# Backup database first
pg_dump -U postgres -d rpa_analyzer > backup_$(date +%Y%m%d).sql

# Run migrations
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

---

## Testing

### Manual Testing with PowerShell

```powershell
# Test health endpoint
Invoke-RestMethod -Uri "http://127.0.0.1:8000/health"

# Test registration
$registerBody = @{
    email = "test@example.com"
    password = "Test123!@#"
    full_name = "Test User"
    company_name = "Test Company"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/auth/register" `
    -Method Post -Body $registerBody -ContentType "application/json"

# Test login
$loginBody = @{
    email = "test@example.com"
    password = "Test123!@#"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/auth/login" `
    -Method Post -Body $loginBody -ContentType "application/json"

$token = $response.access_token

# Test authenticated endpoint
$headers = @{
    Authorization = "Bearer $token"
}

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/user/me" `
    -Headers $headers
```

### Frontend Integration Test

Open `test_frontend.html` in a browser to test:

- Backend connectivity
- User registration
- User login
- Authenticated requests

### Database Verification

```powershell
$env:PGPASSWORD='1234'

# Count users
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -h localhost -d rpa_analyzer -c "SELECT COUNT(*) FROM users;"

# View recent analyses
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -h localhost -d rpa_analyzer -c "SELECT * FROM analysis_history ORDER BY created_at DESC LIMIT 5;"
```

---

## Troubleshooting

### Common Issues

#### 1. ModuleNotFoundError

**Error**: `ModuleNotFoundError: No module named 'app.routes'`

**Solution**: Ensure all `__init__.py` files exist:

```powershell
# Check for missing __init__.py files
Get-ChildItem -Path app -Recurse -Filter "__init__.py"
```

#### 2. Database Connection Failed

**Error**: `password authentication failed for user "postgres"`

**Solution**: Update `.env` and `alembic.ini` with correct credentials:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/rpa_analyzer
```

#### 3. Database Does Not Exist

**Error**: `database "rpa_analyzer" does not exist`

**Solution**: Create the database:

```powershell
$env:PGPASSWORD='1234'
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -h localhost -c "CREATE DATABASE rpa_analyzer;"
```

#### 4. Port Already in Use

**Error**: `Address already in use`

**Solution**: Find and kill the process:

```powershell
# Find process using port 8000
Get-NetTCPConnection -LocalPort 8000

# Kill the process
Stop-Process -Id PROCESS_ID -Force
```

#### 5. CORS Errors

**Error**: `CORS policy: No 'Access-Control-Allow-Origin' header`

**Solution**: Verify CORS middleware is configured in `app/main.py` and backend is running.

#### 6. Password Too Long Error

**Error**: `password cannot be longer than 72 bytes`

**Solution**: This is a bcrypt limitation. Ensure passwords are hashed before storage and not exceeding 72 bytes.

#### 7. Migration Issues

**Error**: `Target database is not up to date`

**Solution**: Run migrations:

```powershell
alembic upgrade head
```

To create a new migration:

```powershell
alembic revision --autogenerate -m "description of changes"
```

---

## Additional Resources

### Documentation Links

- **FastAPI**: https://fastapi.tiangolo.com/
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **Alembic**: https://alembic.sqlalchemy.org/
- **Pydantic**: https://docs.pydantic.dev/
- **PostgreSQL**: https://www.postgresql.org/docs/

### Project Files

- [README.md](file:///c:/Users/sumam/Documents/Migration%20Project/IAAP/backend/BackendV1/README.md) - Quick start guide
- [GITHUB_SETUP.md](file:///c:/Users/sumam/Documents/Migration%20Project/IAAP/backend/BackendV1/GITHUB_SETUP.md) - GitHub setup instructions
- [requirements.txt](file:///c:/Users/sumam/Documents/Migration%20Project/IAAP/backend/BackendV1/requirements.txt) - Python dependencies
- [pyproject.toml](file:///c:/Users/sumam/Documents/Migration%20Project/IAAP/backend/BackendV1/pyproject.toml) - Project configuration

### Support Commands

```powershell
# Start backend
uvicorn app.main:app --reload

# Run migrations
alembic upgrade head

# Create migration
alembic revision --autogenerate -m "description"

# Check database tables
$env:PGPASSWORD='1234'
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -h localhost -d rpa_analyzer -c "\dt"

# View table structure
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -h localhost -d rpa_analyzer -c "\d users"
```

---

## Summary

The **IAAP Backend** is a production-ready FastAPI application providing:

✅ **Complete Authentication System** with JWT and API keys  
✅ **Subscription Management** with tiered plans  
✅ **AI-Powered Analysis** using Google Gemini  
✅ **Admin Dashboard** for system management  
✅ **Comprehensive API** with interactive documentation  
✅ **Database Migrations** with Alembic  
✅ **Security Best Practices** implemented

**Current Status**: Running successfully on http://127.0.0.1:8000

**Next Steps**:

1. Complete frontend integration
2. Implement comprehensive testing
3. Security hardening for production
4. Deploy to production environment

---

**Document Version**: 1.0  
**Last Updated**: January 19, 2026  
**Maintained By**: Development Team
