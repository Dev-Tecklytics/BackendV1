import json
import time
from google import genai
from pydantic import ValidationError

from app.services.analysis.prompts import WORKFLOW_ANALYSIS_PROMPT
from app.core.config import settings
from app.core.usage_tracker import increment_ai_calls


# genai.configure no longer used in new SDK

MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds


def run_workflow_llm_analysis(metrics: dict, platform: str, db, user_id) -> dict:
    """
    Use Gemini AI to analyze workflow and provide insights.
    
    Args:
        metrics: Dictionary containing workflow metrics (activity_count, variable_count, etc.)
        platform: Platform name (e.g., 'uipath', 'automation anywhere')
        db: Database session
        user_id: User ID for tracking AI usage
    
    Returns:
        Dictionary with ai_summary, complexity_explanation, and recommendations
    """
    prompt = WORKFLOW_ANALYSIS_PROMPT.format(
        platform=platform,
        activity_count=metrics.get('activity_count', 0),
        variable_count=metrics.get('variable_count', 0),
        nesting_depth=metrics.get('nesting_depth', 0),
        complexity_score=metrics.get('complexity_score', 0),
        complexity_level=metrics.get('complexity_level', 'Unknown'),
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
                    "max_output_tokens": 512,
                },
            )

            raw_text = response.text.strip()
            parsed = json.loads(raw_text)

            return {
                "ai_summary": parsed.get("summary", ""),
                "complexity_explanation": parsed.get("complexity_explanation", ""),
                "ai_recommendations": parsed.get("recommendations", []),
            }

        except (json.JSONDecodeError, KeyError, ValidationError) as e:
            last_error = e
        except Exception as e:
            last_error = e

        if attempt < MAX_RETRIES:
            time.sleep(RETRY_DELAY)

    # Final fallback (never crash analysis)
    return {
        "ai_summary": "AI analysis temporarily unavailable.",
        "complexity_explanation": "",
        "ai_recommendations": [],
    }
