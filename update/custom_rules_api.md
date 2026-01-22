# Custom Rules API - Quick Reference

## Overview

Complete CRUD API for managing user-defined workflow validation rules.

## Endpoints

### 1. **POST** `/api/v1/custom-rules`

Create a new custom rule

**Request Body:**

```json
{
  "name": "Max Activity Count",
  "rule_type": "activity_count",
  "config": { "threshold": 50 },
  "severity": "high",
  "is_active": true
}
```

**Valid rule_type values:**

- `activity_count` - Validates activity count threshold
- `nesting_depth` - Validates nesting depth threshold
- `regex` - Pattern matching (future)

**Valid severity values:** `low`, `medium`, `high`, `critical`

---

### 2. **GET** `/api/v1/custom-rules/{rule_id}`

Get a specific custom rule

**Response:**

```json
{
  "rule_id": "uuid",
  "user_id": "uuid",
  "name": "Max Activity Count",
  "rule_type": "activity_count",
  "config": { "threshold": 50 },
  "severity": "high",
  "is_active": true,
  "created_at": "2026-01-21T00:00:00Z"
}
```

---

### 3. **GET** `/api/v1/custom-rules`

List all custom rules for authenticated user

**Query Parameters:**

- `rule_type` (optional) - Filter by rule type
- `is_active` (optional) - Filter by active status
- `skip` (default: 0) - Pagination offset
- `limit` (default: 100) - Max results

**Response:**

```json
{
  "total": 5,
  "rules": [...]
}
```

---

### 4. **PUT** `/api/v1/custom-rules/{rule_id}`

Update a custom rule

**Request Body (all fields optional):**

```json
{
  "name": "Updated Name",
  "config": { "threshold": 75 },
  "is_active": false
}
```

---

### 5. **DELETE** `/api/v1/custom-rules/{rule_id}`

Delete a custom rule

**Response:**

```json
{
  "message": "Custom rule deleted successfully",
  "rule_id": "uuid"
}
```

---

### 6. **POST** `/api/v1/custom-rules/validate`

Validate workflow metrics against user's active custom rules

**Request Body:**

```json
{
  "activity_count": 60,
  "nesting_depth": 5,
  "variable_count": 20
}
```

**Response:**

```json
{
  "findings": [
    {
      "rule": "Max Activity Count",
      "severity": "high",
      "message": "Activity count exceeded"
    }
  ],
  "total_violations": 1,
  "rules_checked": 3
}
```

---

## Example Usage

### Create a rule

```bash
curl -X POST "http://localhost:8000/api/v1/custom-rules" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Max Nesting Depth",
    "rule_type": "nesting_depth",
    "config": {"threshold": 3},
    "severity": "medium",
    "is_active": true
  }'
```

### List active rules

```bash
curl "http://localhost:8000/api/v1/custom-rules?is_active=true" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Validate workflow

```bash
curl -X POST "http://localhost:8000/api/v1/custom-rules/validate" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "activity_count": 45,
    "nesting_depth": 4,
    "variable_count": 15
  }'
```

---

## Features

✅ Full CRUD operations
✅ User-scoped rules (each user has their own)
✅ Validation endpoint for workflow checking
✅ Active/inactive toggle
✅ Severity levels
✅ Filtering and pagination
✅ Uses existing CustomRule model and engine

---

## Files Modified

- **Created**: `app/routes/custom_rules.py`
- **Modified**: `app/main.py` (added router registration)
