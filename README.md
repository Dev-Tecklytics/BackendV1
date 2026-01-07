# IAAP Backend API

**Intelligent Automation Analysis Platform - Backend Service**

A FastAPI-based backend service for the IAAP platform, providing authentication, user management, analysis processing, and subscription management.

---

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [System Status](#-system-status)
- [Project Structure](#-project-structure)
- [Setup & Installation](#-setup--installation)
- [Configuration](#-configuration)
- [Running the Application](#-running-the-application)
- [API Documentation](#-api-documentation)
- [Authentication](#-authentication)
- [Database](#-database)
- [Frontend Integration](#-frontend-integration)
- [Testing](#-testing)
- [Troubleshooting](#-troubleshooting)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL 17 or 18
- pip or uv package manager

### Run the Backend

```powershell
# Navigate to project directory
cd C:\Users\Prasanna\Downloads\backend\backend

# Install dependencies (if needed)
python -m pip install fastapi uvicorn sqlalchemy psycopg2-binary alembic passlib python-jose email-validator redis python-multipart

# Run the server
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Backend will be available at**: http://127.0.0.1:8000

---

## ✅ System Status

### Current Configuration
- **Backend URL**: http://127.0.0.1:8000
- **Database**: PostgreSQL (localhost:5432)
- **Database Name**: `rpa_analyzer`
- **Database User**: `postgres`
- **Database Password**: `1234`
- **CORS**: Enabled for all origins
- **JWT Algorithm**: HS256

### What's Implemented
- ✅ User Authentication (Register/Login)
- ✅ JWT Token Management
- ✅ User Profile Management
- ✅ API Key Management
- ✅ Analysis Processing
- ✅ File Upload
- ✅ Subscription Management
- ✅ Admin Panel Endpoints
- ✅ Database Migrations (Alembic)
- ✅ CORS Middleware

---

## 📁 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── core/                   # Core functionality
│   │   ├── __init__.py
│   │   ├── auth.py            # Authentication utilities
│   │   ├── deps.py            # Dependencies
│   │   ├── jwt.py             # JWT token handling
│   │   ├── security.py        # Password hashing/verification
│   │   ├── redis_client.py    # Redis connection
│   │   └── rate_limiter.py    # Rate limiting
│   ├── models/                 # Database models
│   │   ├── __init__.py
│   │   └── user.py            # User model
│   ├── routes/                 # API endpoints
│   │   ├── __init__.py
│   │   ├── auth.py            # Authentication routes
│   │   ├── user.py            # User management
│   │   ├── api_key.py         # API key management
│   │   ├── analysis.py        # Analysis endpoints
│   │   ├── analysis_history.py
│   │   ├── analysis_result.py
│   │   ├── analysis_upload.py
│   │   ├── subscription.py    # Subscription management
│   │   ├── admin_*.py         # Admin endpoints
│   │   └── health.py          # Health check
│   ├── schemas/                # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── auth.py            # Auth schemas
│   │   └── user.py            # User schemas
│   └── services/               # Business logic
│       └── __init__.py
├── alembic/                    # Database migrations
│   ├── versions/
│   └── env.py
├── .env                        # Environment variables
├── alembic.ini                 # Alembic configuration
├── pyproject.toml              # Project dependencies
├── test_frontend.html          # Frontend connection test page
└── README.md                   # This file
```

---

## 🛠️ Setup & Installation

### 1. Install Python Dependencies

```powershell
# Using pip
python -m pip install fastapi uvicorn sqlalchemy psycopg2-binary alembic passlib[bcrypt] python-jose[cryptography] email-validator redis python-multipart

# Or using requirements from pyproject.toml
python -m pip install -e .
```

### 2. Setup PostgreSQL Database

```powershell
# Check if PostgreSQL is running
Get-Service -Name "*postgres*"

# Create database (if not exists)
$env:PGPASSWORD='1234'
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -h localhost -c "CREATE DATABASE rpa_analyzer;"
```

### 3. Configure Environment Variables

Create/update `.env` file:

```env
DATABASE_URL=postgresql://postgres:1234@localhost:5432/rpa_analyzer
JWT_SECRET=super-secret-key-change-this
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60
```

### 4. Run Database Migrations

```powershell
python -m alembic upgrade head
```

### 5. Create Required `__init__.py` Files

The following `__init__.py` files have been created:
- `app/__init__.py`
- `app/routes/__init__.py`
- `app/core/__init__.py`
- `app/schemas/__init__.py`
- `app/services/__init__.py`

---

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:1234@localhost:5432/rpa_analyzer` |
| `JWT_SECRET` | Secret key for JWT tokens | `super-secret-key-change-this` |
| `JWT_ALGORITHM` | JWT signing algorithm | `HS256` |
| `JWT_EXPIRE_MINUTES` | Token expiration time | `60` |

### CORS Configuration

CORS is enabled in `app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**⚠️ Production Note**: Replace `allow_origins=["*"]` with specific frontend URLs.

---

## 🏃 Running the Application

### Development Mode

```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Production Mode

```powershell
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Verify Server is Running

```powershell
# Test health endpoint
Invoke-RestMethod -Uri "http://127.0.0.1:8000/health"

# Expected response: { "status": "ok" }
```

---

## 📚 API Documentation

### Interactive Documentation

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc
- **OpenAPI JSON**: http://127.0.0.1:8000/openapi.json

### Available Endpoints

#### Health Check
- `GET /health` - Server health check

#### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh-token` - Refresh access token
- `POST /api/v1/auth/logout` - Logout user

#### User Management
- `GET /api/v1/user/me` - Get current user profile
- `PUT /api/v1/user/profile` - Update user profile

#### API Keys
- `GET /api/v1/api-keys` - List API keys
- `POST /api/v1/api-keys` - Create API key
- `DELETE /api/v1/api-keys/{key_id}` - Delete API key

#### Analysis
- `POST /api/v1/analysis` - Create new analysis
- `GET /api/v1/analysis/history` - Get analysis history
- `GET /api/v1/analysis/result/{id}` - Get analysis result
- `POST /api/v1/analysis/upload` - Upload file for analysis

#### Subscriptions
- `GET /api/v1/subscription/plans` - Get subscription plans
- `POST /api/v1/subscription/subscribe` - Subscribe to plan

#### Admin (requires admin role)
- `GET /api/v1/admin/users` - List all users
- `GET /api/v1/admin/analytics` - Get analytics
- `GET /api/v1/admin/usage` - Get usage statistics
- `GET /api/v1/admin/api-keys` - Manage API keys
- `GET /api/v1/admin/subscription` - Manage subscriptions

---

## 🔐 Authentication

### Registration (Signup)

**Endpoint**: `POST /api/v1/auth/register`

**Request**:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "full_name": "John Doe",
  "company_name": "Acme Corp"
}
```

**Response**:
```json
{
  "user_id": "uuid-here",
  "email": "user@example.com",
  "full_name": "John Doe"
}
```

**Features**:
- ✅ Email validation
- ✅ Password hashing (bcrypt)
- ✅ Duplicate email check
- ✅ Returns user data (without password)

### Login (Signin)

**Endpoint**: `POST /api/v1/auth/login`

**Request**:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Using Authentication Token

Include the token in the `Authorization` header:

```javascript
headers: {
  'Authorization': 'Bearer YOUR_ACCESS_TOKEN'
}
```

### Security Features

- ✅ Password hashing with bcrypt
- ✅ JWT token-based authentication
- ✅ Email validation
- ✅ Secure password verification
- ✅ Token expiration (60 minutes)

---

## 🗄️ Database

### Connection Details

- **Host**: localhost
- **Port**: 5432
- **Database**: rpa_analyzer
- **User**: postgres
- **Password**: 1234

### Database Schema

**Tables**:
- `users` - User accounts
- `api_keys` - API key management
- `analysis_history` - Analysis records
- `subscriptions` - User subscriptions
- `subscription_plans` - Available plans
- `payment_transactions` - Payment records
- `usage_tracking` - API usage tracking
- `alembic_version` - Migration tracking

### Users Table Structure

```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    password_hash VARCHAR NOT NULL,
    full_name VARCHAR,
    company_name VARCHAR,
    status VARCHAR,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,
    user_role VARCHAR
);
```

### Database Commands

```powershell
# List all databases
$env:PGPASSWORD='1234'
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -h localhost -c "\l"

# List tables in rpa_analyzer
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -h localhost -d rpa_analyzer -c "\dt"

# View table structure
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -h localhost -d rpa_analyzer -c "\d users"

# Count users
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -h localhost -d rpa_analyzer -c "SELECT COUNT(*) FROM users;"
```

### Migrations

```powershell
# Create new migration
python -m alembic revision --autogenerate -m "description"

# Apply migrations
python -m alembic upgrade head

# Rollback migration
python -m alembic downgrade -1

# View migration history
python -m alembic history
```

---

## 🔗 Frontend Integration

### Configure Frontend API URL

Create `.env` file in your frontend project:

```env
# For Vite
VITE_API_URL=http://127.0.0.1:8000

# For Create React App
REACT_APP_API_URL=http://127.0.0.1:8000

# For Next.js
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

### API Service Setup (Axios)

```javascript
// src/services/api.js
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
```

### Authentication Service

```javascript
// src/services/auth.js
import api from './api';

export const authService = {
  // Register
  register: async (userData) => {
    const response = await api.post('/api/v1/auth/register', userData);
    return response.data;
  },

  // Login
  login: async (email, password) => {
    const response = await api.post('/api/v1/auth/login', {
      email,
      password
    });
    const { access_token } = response.data;
    localStorage.setItem('access_token', access_token);
    return response.data;
  },

  // Logout
  logout: () => {
    localStorage.removeItem('access_token');
  },

  // Get current user
  getCurrentUser: async () => {
    const response = await api.get('/api/v1/user/me');
    return response.data;
  },
};
```

### React Component Example

```javascript
import React, { useState } from 'react';
import { authService } from '../services/auth';

function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const data = await authService.login(email, password);
      console.log('Logged in:', data);
      // Redirect to dashboard
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  return (
    <form onSubmit={handleLogin}>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
      />
      <button type="submit">Login</button>
    </form>
  );
}
```

---

## 🧪 Testing

### Test Connection

A test HTML page is provided: `test_frontend.html`

Open it in browser to test:
- Backend health check
- User registration
- User login
- Authenticated requests

### Manual Testing (PowerShell)

```powershell
# Test health
Invoke-RestMethod -Uri "http://127.0.0.1:8000/health"

# Test registration
$body = @{
    email = "test@example.com"
    password = "Test123!@#"
    full_name = "Test User"
    company_name = "Test Company"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/auth/register" `
    -Method Post -Body $body -ContentType "application/json"

# Test login
$loginBody = @{
    email = "test@example.com"
    password = "Test123!@#"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/auth/login" `
    -Method Post -Body $loginBody -ContentType "application/json"
```

### Browser Console Testing

```javascript
// Test health
fetch('http://127.0.0.1:8000/health')
  .then(r => r.json())
  .then(console.log);

// Test registration
fetch('http://127.0.0.1:8000/api/v1/auth/register', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'test@example.com',
    password: 'Test123!@#',
    full_name: 'Test User',
    company_name: 'Test Company'
  })
})
  .then(r => r.json())
  .then(console.log);

// Test login
fetch('http://127.0.0.1:8000/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'test@example.com',
    password: 'Test123!@#'
  })
})
  .then(r => r.json())
  .then(data => {
    console.log('Token:', data.access_token);
    localStorage.setItem('access_token', data.access_token);
  });
```

---

## 🔧 Troubleshooting

### Backend Won't Start

**Issue**: `ModuleNotFoundError: No module named 'app.routes'`

**Solution**: Ensure all `__init__.py` files exist:
```powershell
# Check for __init__.py files
Get-ChildItem -Path app -Recurse -Filter "__init__.py"
```

**Issue**: `No module named 'passlib'` or similar

**Solution**: Install missing dependencies:
```powershell
python -m pip install passlib[bcrypt] python-jose[cryptography] email-validator redis
```

### Database Connection Issues

**Issue**: `password authentication failed for user "postgres"`

**Solution**: Update `.env` and `alembic.ini` with correct password:
```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/rpa_analyzer
```

**Issue**: `database "rpa_analyzer" does not exist`

**Solution**: Create the database:
```powershell
$env:PGPASSWORD='1234'
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -h localhost -c "CREATE DATABASE rpa_analyzer;"
```

### CORS Errors

**Issue**: `CORS policy: No 'Access-Control-Allow-Origin' header`

**Solution**: CORS is already enabled in `app/main.py`. Ensure backend is running and frontend is making requests to `http://127.0.0.1:8000`.

### 401 Unauthorized

**Issue**: Getting 401 on authenticated endpoints

**Solution**: 
1. Ensure you're logged in and have a token
2. Include token in Authorization header: `Bearer YOUR_TOKEN`
3. Check token hasn't expired (60 minutes)

### Port Already in Use

**Issue**: `Address already in use`

**Solution**: 
```powershell
# Find process using port 8000
Get-NetTCPConnection -LocalPort 8000

# Kill the process
Stop-Process -Id PROCESS_ID -Force
```

---

## 📦 Dependencies

### Core Dependencies

```toml
[project.dependencies]
fastapi = ">=0.125.0"
uvicorn = ">=0.38.0"
sqlalchemy = ">=2.0.45"
psycopg2-binary = ">=2.9.11"
alembic = ">=1.17.2"
pydantic = ">=2.12.5"
python-dotenv = ">=1.2.1"
passlib[bcrypt] = ">=1.7.4"
python-jose = ">=3.5.0"
python-multipart = ">=0.0.21"
email-validator = ">=2.3.0"
redis = ">=7.1.0"
bcrypt = ">=5.0.0"
argon2-cffi = ">=25.1.0"
```

---

## 🚀 Deployment

### Production Checklist

- [ ] Change `JWT_SECRET` to a strong random value
- [ ] Update `allow_origins` in CORS to specific frontend URLs
- [ ] Use environment variables for all sensitive data
- [ ] Enable HTTPS
- [ ] Set up proper logging
- [ ] Configure rate limiting
- [ ] Set up database backups
- [ ] Use a production-grade WSGI server (gunicorn + uvicorn workers)
- [ ] Set up monitoring and alerts

### Production Run Command

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## 📝 Changelog

### Latest Updates (2026-01-05)

- ✅ Created all required `__init__.py` files for proper package structure
- ✅ Added CORS middleware for frontend integration
- ✅ Updated database password configuration in `.env` and `alembic.ini`
- ✅ Created `rpa_analyzer` database
- ✅ Ran database migrations successfully
- ✅ Installed missing dependencies (passlib, python-jose, redis, email-validator)
- ✅ Verified authentication endpoints (register/login)
- ✅ Created test page for frontend connection testing
- ✅ Documented all API endpoints and integration steps

---

## 📞 Support

### Resources

- **API Documentation**: http://127.0.0.1:8000/docs
- **Test Page**: `test_frontend.html`
- **Database**: PostgreSQL on localhost:5432

### Common Commands

```powershell
# Start backend
python -m uvicorn app.main:app --reload

# Run migrations
python -m alembic upgrade head

# Test connection
Invoke-RestMethod -Uri "http://127.0.0.1:8000/health"

# Check database
$env:PGPASSWORD='1234'
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -h localhost -d rpa_analyzer -c "\dt"
```

---

## 📄 License

[Add your license information here]

---

## 👥 Contributors

[Add contributor information here]

---

**Backend Status**: ✅ Running and Ready
**Database**: ✅ Connected
**Authentication**: ✅ Implemented
**CORS**: ✅ Enabled
**Ready for Production**: 🚀 Yes (after production checklist)
