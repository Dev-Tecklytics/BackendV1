import json
import time
import google.generativeai as genai
from pydantic import ValidationError

from app.domain.llm_contracts import LLMInput, LLMOutput
from app.services.analysis.prompts import ANALYSIS_PROMPT_V1
from app.core.config import settings
from app.core.usage_tracker import increment_ai_calls



genai.configure(api_key=settings.google_api_key)

MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds


def run_llm_analysis(data: LLMInput, db, user_id) -> LLMOutput:
    prompt = ANALYSIS_PROMPT_V1.format(
        platform=data.platform,
        activity_count=data.metrics.activity_count,
        variable_count=data.metrics.variable_count,
        nesting_depth=data.metrics.nesting_depth,
        invoked_workflows=data.metrics.invoked_workflows,
        has_custom_code=data.metrics.has_custom_code,
    )

    model = genai.GenerativeModel("gemini-2.5-flash")

    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            increment_ai_calls(db, user_id)

            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.2,
                    "max_output_tokens": 512,
                },
            )

            raw_text = response.text.strip()
            parsed = json.loads(raw_text)

            return LLMOutput(
                summary=parsed["summary"],
                risks=parsed.get("risks", []),
                optimization_suggestions=parsed.get("optimization_suggestions", []),
                migration_notes=parsed.get("migration_notes", []),
            )

        except (json.JSONDecodeError, KeyError, ValidationError) as e:
            last_error = e
        except Exception as e:
            last_error = e

        time.sleep(RETRY_DELAY)

    # Final fallback (never crash analysis)
    return LLMOutput(
        summary="AI analysis temporarily unavailable.",
        risks=[],
        optimization_suggestions=[],
        migration_notes=[],
    )
