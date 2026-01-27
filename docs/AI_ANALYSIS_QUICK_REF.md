# AI Code Review Analysis - Quick Reference

## 🚀 Quick Start

### 1. Run Migration

```bash
uv run alembic upgrade head
```

### 2. Start Server

```bash
uv run uvicorn app.main:app --reload
```

### 3. Use API

**Run AI Analysis:**

```bash
POST /api/v1/code-review/{review_id}/ai-analysis
```

**Get AI Analysis:**

```bash
GET /api/v1/code-review/{review_id}/ai-analysis
```

## 📁 Files Created

### Models

- `app/models/ai_code_review.py` - AICodeReviewAnalysis, AIInsight models
- `app/models/audit_log.py` - AuditLog model

### Services

- `app/services/code_review/ai_code_review_service.py` - AI analysis logic

### Routes

- `app/routes/code_review.py` - Updated with new endpoints

### Database

- Migration: `alembic/versions/*_add_ai_code_review_analysis_tables.py`

### Documentation

- `docs/AI_CODE_REVIEW_ANALYSIS.md` - Full documentation
- `test_ai_analysis.py` - Test script

## 🔑 Key Features

✅ **Comprehensive Analysis**

- Design patterns & anti-patterns
- Optimization opportunities
- Migration risks
- Estimated impact scores
- Categorized insights

✅ **Production Ready**

- Error handling & retries
- Response validation
- Caching for performance
- Audit logging
- Type safety with Pydantic

✅ **Gemini 2.5 Flash Integration**

- Structured JSON responses
- Temperature: 0.3 for consistency
- Max tokens: 4000
- 3 retry attempts

## 📊 Response Structure

```json
{
  "analysis": {
    "overallAssessment": "string",
    "patterns": {
      "identified": ["string"],
      "antiPatterns": ["string"]
    },
    "optimizationOpps": ["string"],
    "migrationRisks": ["string"],
    "estimatedImpact": {
      "maintainability": 0-100,
      "performance": 0-100,
      "reliability": 0-100
    },
    "insights": [{
      "category": "Architecture|Performance|Maintainability|ErrorHandling|Security|BestPractices",
      "severity": "Critical|Major|Minor|Info",
      "title": "string",
      "description": "string",
      "recommendation": "string",
      "reasoning": "string",
      "confidence": 0.0-1.0,
      "relatedActivities": ["string"]
    }]
  }
}
```

## 🔧 Environment Variables

Required in `.env`:

```env
GOOGLE_API_KEY=your_gemini_api_key
DATABASE_URL=postgresql://...
JWT_SECRET=your_secret_key
```

## 🧪 Testing

```bash
# Update credentials in test_ai_analysis.py
python test_ai_analysis.py
```

## ⚡ Common Commands

```bash
# Create migration
uv run alembic revision --autogenerate -m "migration_name"

# Apply migrations
uv run alembic upgrade head

# Rollback migration
uv run alembic downgrade -1

# Check current migration
uv run alembic current

# Start server
uv run uvicorn app.main:app --reload

# Start server with custom port
uv run uvicorn app.main:app --reload --port 8080
```

## 🐛 Troubleshooting

| Issue             | Solution                                              |
| ----------------- | ----------------------------------------------------- |
| Import errors     | Restart server: `Ctrl+C` then restart                 |
| Migration errors  | Check database connection, run `alembic upgrade head` |
| AI analysis fails | Verify `GOOGLE_API_KEY` in `.env`                     |
| 404 on endpoints  | Ensure code review exists, check review_id            |
| Database errors   | Run migrations, check PostgreSQL is running           |

## 📈 Performance Tips

- **Caching**: Analysis is cached per review_id
- **Batch Processing**: Consider background jobs for large batches
- **Token Optimization**: Prompt is optimized to minimize tokens
- **Retry Logic**: Handles transient failures automatically

## 🔐 Security Notes

- All endpoints require authentication
- Audit logs track all AI operations
- No sensitive data in error messages
- User context maintained throughout

## 📞 Support

For issues or questions:

1. Check `docs/AI_CODE_REVIEW_ANALYSIS.md` for detailed docs
2. Review error logs in console
3. Check database migrations are applied
4. Verify environment variables

---

**Quick Links:**

- Full Documentation: `docs/AI_CODE_REVIEW_ANALYSIS.md`
- Test Script: `test_ai_analysis.py`
- Models: `app/models/ai_code_review.py`
- Service: `app/services/code_review/ai_code_review_service.py`
