# Get Files by Project ID - API Documentation

## Endpoint

**GET** `/api/v1/workflows/files/{project_id}`

Get all files associated with a specific project, including their workflow analysis data if available.

---

## Request

### Headers

```
Authorization: Bearer <access_token>
```

### Path Parameters

| Parameter    | Type | Required | Description                          |
| ------------ | ---- | -------- | ------------------------------------ |
| `project_id` | UUID | Yes      | The unique identifier of the project |

### Example Request

```bash
curl -X GET "http://127.0.0.1:8000/api/v1/workflows/files/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

## Response

### Success Response (200 OK)

```json
{
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "project_name": "My RPA Project",
  "platform": "UiPath",
  "total_files": 2,
  "files": [
    {
      "file_id": "660e8400-e29b-41d4-a716-446655440001",
      "project_id": "550e8400-e29b-41d4-a716-446655440000",
      "file_name": "Main.xaml",
      "file_path": "uploads/660e8400-e29b-41d4-a716-446655440001_Main.xaml",
      "file_size": 15420,
      "uploaded_at": "2026-01-24T15:30:00Z",
      "workflow": {
        "workflow_id": "770e8400-e29b-41d4-a716-446655440002",
        "platform": "UiPath",
        "complexity_score": 45,
        "complexity_level": "Medium",
        "activity_count": 25,
        "nesting_depth": 3,
        "variable_count": 10,
        "invoked_workflows": 2,
        "has_custom_code": false,
        "estimated_effort_hours": 12,
        "compatibility_score": 85,
        "risk_indicators": ["High nesting depth (level 3)"],
        "activity_breakdown": {
          "Data Manipulation": 8,
          "UI Automation": 12,
          "Control Flow": 5
        },
        "suggestions": [
          {
            "id": 1,
            "priority": "medium",
            "title": "Reduce complexity",
            "description": "Consider breaking down into smaller workflows",
            "impact": "Medium",
            "effort": "Medium",
            "benefits": ["Improved maintainability"],
            "implementation_steps": ["Refactor into modules"]
          }
        ],
        "ai_summary": "This workflow handles user login automation...",
        "ai_recommendations": [
          "Add error handling for network failures",
          "Implement retry logic"
        ],
        "analyzed_at": "2026-01-24T15:35:00Z"
      }
    },
    {
      "file_id": "660e8400-e29b-41d4-a716-446655440003",
      "project_id": "550e8400-e29b-41d4-a716-446655440000",
      "file_name": "ProcessInvoice.xaml",
      "file_path": "uploads/660e8400-e29b-41d4-a716-446655440003_ProcessInvoice.xaml",
      "file_size": 8920,
      "uploaded_at": "2026-01-24T16:00:00Z",
      "workflow": null
    }
  ]
}
```

### Response Fields

#### Root Level

| Field          | Type          | Description                              |
| -------------- | ------------- | ---------------------------------------- |
| `project_id`   | string (UUID) | The project identifier                   |
| `project_name` | string        | Name of the project                      |
| `platform`     | string        | Platform type (UiPath, Blue Prism, etc.) |
| `total_files`  | integer       | Total number of files in the project     |
| `files`        | array         | Array of file objects                    |

#### File Object

| Field         | Type              | Description                       |
| ------------- | ----------------- | --------------------------------- |
| `file_id`     | string (UUID)     | Unique file identifier            |
| `project_id`  | string (UUID)     | Parent project identifier         |
| `file_name`   | string            | Original filename                 |
| `file_path`   | string            | Server storage path               |
| `file_size`   | integer           | File size in bytes                |
| `uploaded_at` | string (ISO 8601) | Upload timestamp                  |
| `workflow`    | object or null    | Associated workflow analysis data |

#### Workflow Object (if analyzed)

| Field                    | Type              | Description                      |
| ------------------------ | ----------------- | -------------------------------- |
| `workflow_id`            | string (UUID)     | Workflow identifier              |
| `platform`               | string            | Platform type                    |
| `complexity_score`       | integer           | Calculated complexity score      |
| `complexity_level`       | string            | Low/Medium/High/Very High        |
| `activity_count`         | integer           | Number of activities             |
| `nesting_depth`          | integer           | Maximum nesting level            |
| `variable_count`         | integer           | Number of variables              |
| `invoked_workflows`      | integer           | Number of invoked workflows      |
| `has_custom_code`        | boolean/JSON      | Custom code detection            |
| `estimated_effort_hours` | integer           | Migration effort estimate        |
| `compatibility_score`    | integer           | Compatibility percentage (0-100) |
| `risk_indicators`        | array             | List of detected risks           |
| `activity_breakdown`     | object            | Activity categorization          |
| `suggestions`            | array             | Improvement suggestions          |
| `ai_summary`             | string or null    | AI-generated summary             |
| `ai_recommendations`     | array or null     | AI recommendations               |
| `analyzed_at`            | string (ISO 8601) | Analysis timestamp               |

---

## Error Responses

### 404 Not Found

**Scenario:** Project does not exist

```json
{
  "detail": "Project not found"
}
```

### 401 Unauthorized

**Scenario:** Invalid or missing authentication token

```json
{
  "detail": "Not authenticated"
}
```

---

## Use Cases

### 1. Display Project Files in UI

```javascript
// Frontend example
async function loadProjectFiles(projectId) {
  const response = await fetch(
    `http://127.0.0.1:8000/api/v1/workflows/files/${projectId}`,
    {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    },
  );

  const data = await response.json();

  // Display files with their analysis status
  data.files.forEach((file) => {
    console.log(`File: ${file.file_name}`);
    if (file.workflow) {
      console.log(`  Analyzed: Yes`);
      console.log(`  Complexity: ${file.workflow.complexity_level}`);
      console.log(`  Score: ${file.workflow.complexity_score}`);
    } else {
      console.log(`  Analyzed: No`);
    }
  });
}
```

### 2. Check Analysis Status

```python
# Backend example
import requests

def check_project_analysis_status(project_id, token):
    response = requests.get(
        f"http://127.0.0.1:8000/api/v1/workflows/files/{project_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    data = response.json()

    analyzed = sum(1 for f in data['files'] if f['workflow'] is not None)
    total = data['total_files']

    print(f"Analysis Progress: {analyzed}/{total} files analyzed")

    return analyzed, total
```

### 3. Export Project Summary

```javascript
// Generate project summary report
async function generateProjectSummary(projectId) {
  const response = await fetch(
    `http://127.0.0.1:8000/api/v1/workflows/files/${projectId}`,
    {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    },
  );

  const data = await response.json();

  const summary = {
    projectName: data.project_name,
    platform: data.platform,
    totalFiles: data.total_files,
    analyzedFiles: data.files.filter((f) => f.workflow).length,
    totalComplexity: data.files
      .filter((f) => f.workflow)
      .reduce((sum, f) => sum + f.workflow.complexity_score, 0),
    totalEffort: data.files
      .filter((f) => f.workflow)
      .reduce((sum, f) => sum + (f.workflow.estimated_effort_hours || 0), 0),
  };

  return summary;
}
```

---

## Notes

1. **Performance:** This endpoint performs a database query for each file to fetch associated workflow data. For projects with many files (>100), consider implementing pagination.

2. **Null Workflows:** Files that haven't been analyzed will have `workflow: null`. This is normal for newly uploaded files.

3. **Authentication:** This endpoint requires a valid JWT token. Ensure the user has access to the requested project.

4. **File Paths:** The `file_path` field contains the server-side storage path. Do not expose this directly to end users in production.

---

## Related Endpoints

- **GET** `/api/v1/projects/{project_id}` - Get project details
- **GET** `/api/v1/workflows` - List all workflows (with optional project filter)
- **POST** `/api/v1/analyze/upload` - Upload and analyze a file
- **GET** `/api/v1/workflows/{workflow_id}` - Get specific workflow details

---

**Last Updated:** 2026-01-24  
**API Version:** v1
