# AI Code Review Analysis - Implementation Documentation

## 📋 Overview

This implementation provides comprehensive AI-powered code review analysis for RPA workflows using Google Gemini 2.5 Flash. The system analyzes workflows and provides structured insights about design patterns, optimization opportunities, migration risks, and detailed recommendations.

## 🏗️ Architecture

### Components

1. **Database Models** (`app/models/ai_code_review.py`)
   - `AICodeReviewAnalysis`: Stores overall analysis results
   - `AIInsight`: Individual insights with detailed recommendations
   - `AuditLog`: Tracks AI analysis operations

2. **AI Service** (`app/services/code_review/ai_code_review_service.py`)
   - `perform_ai_code_review_sync()`: Main analysis function
   - `build_analysis_prompt()`: Constructs comprehensive prompts
   - `normalize_ai_response()`: Validates and normalizes AI responses

3. **API Routes** (`app/routes/code_review.py`)
   - `POST /api/v1/code-review/{review_id}/ai-analysis`: Run AI analysis
   - `GET /api/v1/code-review/{review_id}/ai-analysis`: Retrieve cached analysis

## 📊 Database Schema

### AICodeReviewAnalysis Table

```sql
CREATE TABLE ai_code_review_analysis (
    id UUID PRIMARY KEY,
    review_id UUID UNIQUE NOT NULL REFERENCES code_reviews(review_id) ON DELETE CASCADE,
    overall_assessment TEXT NOT NULL,
    patterns JSONB NOT NULL,  -- {identified: [], antiPatterns: []}
    optimization_opps JSONB NOT NULL,  -- Array of strings
    migration_risks JSONB NOT NULL,  -- Array of strings
    estimated_impact JSONB NOT NULL,  -- {maintainability, performance, reliability}
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);
```

### AIInsight Table

```sql
CREATE TABLE ai_insights (
    id UUID PRIMARY KEY,
    analysis_id UUID NOT NULL REFERENCES ai_code_review_analysis(id) ON DELETE CASCADE,
    category VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    recommendation TEXT NOT NULL,
    reasoning TEXT NOT NULL,
    confidence FLOAT NOT NULL,
    related_activities JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### AuditLog Table

```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id VARCHAR(255),
    success BOOLEAN DEFAULT TRUE,
    details JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 🔌 API Endpoints

### POST /api/v1/code-review/{review_id}/ai-analysis

Run comprehensive AI analysis on an existing code review.

**Request:**

```http
POST /api/v1/code-review/{review_id}/ai-analysis
Authorization: Bearer <token>
```

**Response (Success - 200):**

```json
{
  "message": "AI analysis completed successfully",
  "analysis": {
    "id": "uuid",
    "reviewId": "uuid",
    "overallAssessment": "Comprehensive assessment text...",
    "patterns": {
      "identified": ["Pattern 1", "Pattern 2"],
      "antiPatterns": ["Anti-pattern 1"]
    },
    "optimizationOpps": ["Optimization 1", "Optimization 2"],
    "migrationRisks": ["Risk 1", "Risk 2"],
    "estimatedImpact": {
      "maintainability": 75,
      "performance": 80,
      "reliability": 85
    },
    "insights": [
      {
        "id": "uuid",
        "category": "Architecture",
        "severity": "Major",
        "title": "Insight title",
        "description": "Detailed description",
        "recommendation": "Specific recommendation",
        "reasoning": "Why this matters",
        "confidence": 0.85,
        "relatedActivities": ["Activity1", "Activity2"]
      }
    ],
    "createdAt": "2026-01-27T12:00:00Z"
  },
  "summary": "Combined Analysis: 15 rule-based findings and 5 AI insights identified",
  "cached": false
}
```

**Response (Cached - 200):**

```json
{
  "message": "AI analysis already exists (cached)",
  "analysis": { ... },
  "cached": true
}
```

**Error Responses:**

- `404`: Code review not found
- `500`: AI analysis failed or database error

### GET /api/v1/code-review/{review_id}/ai-analysis

Retrieve existing AI analysis for a code review.

**Request:**

```http
GET /api/v1/code-review/{review_id}/ai-analysis
Authorization: Bearer <token>
```

**Response (Success - 200):**

```json
{
  "id": "uuid",
  "reviewId": "uuid",
  "overallAssessment": "...",
  "patterns": { ... },
  "optimizationOpps": [ ... ],
  "migrationRisks": [ ... ],
  "estimatedImpact": { ... },
  "insights": [ ... ],
  "createdAt": "2026-01-27T12:00:00Z",
  "updatedAt": "2026-01-27T12:00:00Z"
}
```

**Error Responses:**

- `404`: AI analysis not found (run POST first)

## 🤖 AI Analysis Process

### 1. Data Collection

The system gathers comprehensive workflow data:

- Workflow metrics (activities, nesting depth, variables)
- Activity breakdown by category
- Variables and arguments
- Invoked workflows
- Exception handlers
- Rule-based findings count

### 2. Prompt Construction

A detailed prompt is constructed including:

- Workflow overview and metrics
- Platform-specific context (UiPath/BluePrism)
- Activity distribution
- Sample variables
- Analysis focus areas

### 3. AI Processing

Using Gemini 2.5 Flash with:

- Temperature: 0.3 (for consistency)
- Max tokens: 4000
- JSON response format enforced
- 3 retry attempts with 2-second delays

### 4. Response Validation

The AI response is:

- Parsed and validated
- Normalized to ensure all required fields exist
- Validated using Pydantic models
- Stored in structured database tables

### 5. Caching

Results are cached to:

- Avoid redundant AI calls
- Reduce costs
- Improve response times
- Maintain consistency

## 🎯 Insight Categories

The AI analyzes workflows across multiple dimensions:

1. **Architecture**: Design patterns, modularity, structure
2. **Performance**: Bottlenecks, optimization opportunities
3. **Maintainability**: Code organization, naming, reusability
4. **ErrorHandling**: Exception handling, robustness
5. **Security**: Credential management, data exposure
6. **BestPractices**: Platform-specific recommendations

## 📈 Severity Levels

Insights are classified by severity:

- **Critical**: Must fix - serious issues affecting functionality
- **Major**: Should fix - significant impact on quality
- **Minor**: Nice to fix - minor improvements
- **Info**: Informational - suggestions and observations

## 🔒 Security & Compliance

### Authentication

- All endpoints require valid JWT token
- User authentication via `get_current_user` dependency

### Audit Logging

- All AI analysis operations are logged
- Includes user ID, resource IDs, and operation details
- Failures don't prevent analysis completion

### Data Privacy

- Workflow data is processed securely
- AI responses are validated before storage
- No sensitive data exposed in logs

## 🚀 Usage Example

### Complete Workflow

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"
headers = {"Authorization": "Bearer YOUR_TOKEN"}

# 1. Upload and analyze workflow
upload_response = requests.post(
    f"{BASE_URL}/workflows/uipath",
    files={"file": open("workflow.xaml", "rb")},
    headers=headers
)
workflow_id = upload_response.json()["workflow_id"]

# 2. Run code review
review_response = requests.post(
    f"{BASE_URL}/code-review",
    params={"workflow_id": workflow_id},
    headers=headers
)
review_id = review_response.json()["review_id"]

# 3. Run AI analysis
ai_response = requests.post(
    f"{BASE_URL}/code-review/{review_id}/ai-analysis",
    headers=headers
)
analysis = ai_response.json()["analysis"]

# 4. Retrieve cached analysis later
cached_response = requests.get(
    f"{BASE_URL}/code-review/{review_id}/ai-analysis",
    headers=headers
)
```

## ⚙️ Configuration

### Environment Variables

Required in `.env`:

```env
GOOGLE_API_KEY=your_gemini_api_key
DATABASE_URL=postgresql://...
JWT_SECRET=your_secret_key
```

### AI Model Configuration

In `ai_code_review_service.py`:

```python
MODEL_NAME = "gemini-2.0-flash-exp"  # Gemini 2.5 Flash
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds
```

## 🧪 Testing

### Run Test Script

```bash
# Update credentials in test_ai_analysis.py first
python test_ai_analysis.py
```

### Manual Testing

1. Start the server:

   ```bash
   uv run uvicorn app.main:app --reload
   ```

2. Upload a workflow and get review_id

3. Test AI analysis:

   ```bash
   curl -X POST http://localhost:8000/api/v1/code-review/{review_id}/ai-analysis \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

4. Retrieve analysis:
   ```bash
   curl -X GET http://localhost:8000/api/v1/code-review/{review_id}/ai-analysis \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

## 📝 Migration

The database migration was created automatically:

```bash
# Create migration
uv run alembic revision --autogenerate -m "add_ai_code_review_analysis_tables"

# Apply migration
uv run alembic upgrade head
```

## 🐛 Troubleshooting

### Common Issues

1. **"AI analysis failed"**
   - Check GOOGLE_API_KEY is set correctly
   - Verify API quota/limits
   - Check network connectivity

2. **"Code review not found"**
   - Ensure code review exists for the workflow
   - Run POST /api/v1/code-review first

3. **Database errors**
   - Run migrations: `uv run alembic upgrade head`
   - Check database connectivity

4. **Import errors**
   - Restart the server to reload modules
   - Check all dependencies are installed

## 📊 Performance Considerations

### Optimization Strategies

1. **Caching**: Results are cached per review_id
2. **Async Processing**: Can be extended for background processing
3. **Retry Logic**: Handles transient API failures
4. **Token Limits**: Prompt optimized to stay within limits

### Expected Performance

- AI analysis: 5-15 seconds (depending on workflow size)
- Cached retrieval: <100ms
- Database storage: <500ms

## 🔄 Future Enhancements

Potential improvements:

1. **Background Processing**: Queue AI analysis for large batches
2. **Incremental Analysis**: Only analyze changed workflows
3. **Custom Prompts**: Allow users to customize analysis focus
4. **Comparison**: Compare analyses across workflow versions
5. **Export**: Generate PDF reports from analysis
6. **Webhooks**: Notify when analysis completes

## 📚 References

- [Google Gemini API Documentation](https://ai.google.dev/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

---

**Version**: 1.0.0  
**Last Updated**: 2026-01-27  
**Author**: Dev-Tecklytics Team
