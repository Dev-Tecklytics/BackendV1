# Gemini API Integration for Workflow Analysis and Code Review

## Overview

Integrate Gemini AI into two existing endpoints to provide intelligent, AI-powered analysis:

1. **Workflow Analysis** - Enhance `POST /api/v1/workflows/analyze` with AI insights
2. **Code Review** - Enhance `POST /api/v1/code-review` with AI-powered review suggestions

Both endpoints currently use rule-based/metric-based analysis. We'll augment them with Gemini AI while keeping the existing logic as fallback.

## User Review Required

> [!IMPORTANT]
> **Database Schema Changes**: We need to add AI-generated fields to the `workflows` and `code_reviews` tables. This requires a new Alembic migration.

> [!WARNING]
> **AI Usage Tracking**: All Gemini API calls will increment the `ai_calls_count` for the user. Ensure this aligns with your billing/quota model.

## Proposed Changes

### AI Services Layer

#### [NEW] [workflow_llm_gateway.py](file:///c:/Users/sumam/Documents/Migration%20Project/IAAP/backend/BackendV1/app/services/workflows/workflow_llm_gateway.py)

- New Gemini service for workflow analysis
- Function: `run_workflow_llm_analysis(metrics: dict, platform: str, db, user_id) -> dict`
- Returns: AI-generated insights (summary, complexity_explanation, recommendations)
- Uses `gemini-2.5-flash` model with retry logic
- Tracks AI usage via `increment_ai_calls()`

#### [NEW] [code_review_llm_gateway.py](file:///c:/Users/sumam/Documents/Migration%20Project/IAAP/backend/BackendV1/app/services/code_review/code_review_llm_gateway.py)

- New Gemini service for code review
- Function: `run_code_review_llm(metrics: dict, db, user_id) -> dict`
- Returns: AI-generated review (issues, best_practices, security_concerns, refactoring_suggestions)
- Uses `gemini-2.5-flash` model with retry logic
- Tracks AI usage via `increment_ai_calls()`

---

### Prompt Templates

#### [MODIFY] [prompts.py](file:///c:/Users/sumam/Documents/Migration%20Project/IAAP/backend/BackendV1/app/services/analysis/prompts.py)

- Add `WORKFLOW_ANALYSIS_PROMPT` for workflow insights
- Add `CODE_REVIEW_PROMPT` for code review analysis
- Both prompts enforce JSON-only responses with strict schema

---

### Database Models

#### [MODIFY] [workflow.py](file:///c:/Users/sumam/Documents/Migration%20Project/IAAP/backend/BackendV1/app/models/workflow.py)

- Add `ai_summary` (String) - AI-generated workflow summary
- Add `ai_recommendations` (JSON) - AI suggestions for optimization

#### [MODIFY] [code_review.py](file:///c:/Users/sumam/Documents/Migration%20Project/IAAP/backend/BackendV1/app/models/code_review.py)

- Add `ai_issues` (JSON) - AI-detected issues
- Add `ai_best_practices` (JSON) - AI best practice suggestions
- Add `ai_security_concerns` (JSON) - AI security recommendations

---

### API Routes

#### [MODIFY] [workflows.py](file:///c:/Users/sumam/Documents/Migration%20Project/IAAP/backend/BackendV1/app/routes/workflows.py)

- Import `run_workflow_llm_analysis` from new gateway
- Call Gemini service after local complexity analysis
- Merge AI results with existing metrics
- Add try-catch for graceful degradation if AI fails

#### [MODIFY] [code_review.py](file:///c:/Users/sumam/Documents/Migration%20Project/IAAP/backend/BackendV1/app/routes/code_review.py)

- Import `run_code_review_llm` from new gateway
- Call Gemini service after rule-based review
- Merge AI findings with existing rule-based findings
- Add try-catch for graceful degradation if AI fails

---

### Database Migration

#### [NEW] [alembic/versions/add_ai_fields_to_workflows_and_reviews.py](file:///c:/Users/sumam/Documents/Migration%20Project/IAAP/backend/BackendV1/alembic/versions/add_ai_fields_to_workflows_and_reviews.py)

- Add columns to `workflows`: `ai_summary`, `ai_recommendations`
- Add columns to `code_reviews`: `ai_issues`, `ai_best_practices`, `ai_security_concerns`

---

### Utility Updates

#### [MODIFY] [usage_tracker.py](file:///c:/Users/sumam/Documents/Migration%20Project/IAAP/backend/BackendV1/app/core/usage_tracker.py)

- Add missing `_get_or_create_usage()` helper function (currently referenced but not defined)

## Verification Plan

### Automated Tests

Since no existing test files were found in the codebase, we'll verify through manual API testing:

### Manual Verification

1. **Test Workflow Analysis Endpoint**

   ```bash
   # Start the server
   cd "c:\Users\sumam\Documents\Migration Project\IAAP\backend\BackendV1"
   python -m uvicorn app.main:app --reload

   # Make API request (use existing file_id and valid auth)
   curl -X POST "http://localhost:8000/api/v1/workflows/analyze" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"file_id": "VALID_FILE_UUID", "platform": "uipath"}'
   ```

   - ✅ Verify response includes AI fields: `ai_summary`, `ai_recommendations`
   - ✅ Verify existing fields still present: `complexity_score`, `activity_count`, etc.
   - ✅ Check database: `workflows` table has new AI columns populated

2. **Test Code Review Endpoint**

   ```bash
   # Make API request (use existing workflow_id and valid auth)
   curl -X POST "http://localhost:8000/api/v1/code-review" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"workflow_id": "VALID_WORKFLOW_UUID"}'
   ```

   - ✅ Verify response includes AI fields: `ai_issues`, `ai_best_practices`, `ai_security_concerns`
   - ✅ Verify existing fields still present: `overall_score`, `grade`, `findings`
   - ✅ Check database: `code_reviews` table has new AI columns populated

3. **Test AI Usage Tracking**

   ```bash
   # Check AI analytics endpoint
   curl -X GET "http://localhost:8000/api/v1/admin/ai-analytics/summary" \
     -H "Authorization: Bearer ADMIN_TOKEN"
   ```

   - ✅ Verify `total_ai_calls` increments after each AI-powered analysis
   - ✅ Verify user-specific AI call counts update correctly

4. **Test Error Handling**
   - ✅ Temporarily set invalid `GOOGLE_API_KEY` in `.env`
   - ✅ Call both endpoints and verify they still return results (without AI fields)
   - ✅ Verify no 500 errors, graceful degradation works

5. **Database Migration**

   ```bash
   # Run migration
   alembic upgrade head

   # Verify schema
   # Check that new columns exist in workflows and code_reviews tables
   ```

> [!NOTE]
> **USER ACTION REQUIRED**: After implementation, please test the endpoints using your existing authentication tokens and valid file/workflow UUIDs from your database.
