import json
import time
from google import genai
from pydantic import ValidationError

from app.services.analysis.prompts import CODE_REVIEW_PROMPT
from app.core.config import settings
from app.core.usage_tracker import increment_ai_calls


# genai.configure no longer used in new SDK

MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds


def run_code_review_llm(workflow_metrics: dict, existing_findings: list, db, user_id) -> dict:
    """
    Use Gemini AI to perform code review on workflow.
    
    Args:
        workflow_metrics: Dictionary containing workflow metrics
        existing_findings: List of findings from rule-based review
        db: Database session
        user_id: User ID for tracking AI usage
    
    Returns:
        Dictionary with ai_issues, best_practices, security_concerns, refactoring_suggestions
    """
    # Format existing findings for the prompt
    findings_text = json.dumps(existing_findings, indent=2) if existing_findings else "No rule-based findings"
    
    prompt = CODE_REVIEW_PROMPT.format(
        activity_count=workflow_metrics.get('activity_count', 0),
        variable_count=workflow_metrics.get('variable_count', 0),
        nesting_depth=workflow_metrics.get('nesting_depth', 0),
        complexity_score=workflow_metrics.get('complexity_score', 0),
        overall_score=workflow_metrics.get('overall_score', 0),
        grade=workflow_metrics.get('grade', 'N/A'),
        existing_findings=findings_text,
    )
    client = genai.Client(api_key=settings.google_api_key)
    
    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            increment_ai_calls(db, user_id)

            response = client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=prompt,
                config={
                    "temperature": 0.2,
                    "max_output_tokens": 768,
                },
            )

            raw_text = response.text.strip()
            parsed = json.loads(raw_text)

            return {
                "ai_issues": parsed.get("ai_issues", []),
                "ai_best_practices": parsed.get("best_practices", []),
                "ai_security_concerns": parsed.get("security_concerns", []),
                "ai_refactoring_suggestions": parsed.get("refactoring_suggestions", []),
            }

        except (json.JSONDecodeError, KeyError, ValidationError) as e:
            last_error = e
        except Exception as e:
            last_error = e

        if attempt < MAX_RETRIES:
            time.sleep(RETRY_DELAY)

    # Final fallback (never crash review)
    return {
        "ai_issues": [],
        "ai_best_practices": [],
        "ai_security_concerns": [],
        "ai_refactoring_suggestions": [],
    }
