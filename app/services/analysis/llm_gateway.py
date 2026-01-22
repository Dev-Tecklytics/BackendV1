import json
import time
import re
import logging
from google import genai
from google.genai import types
from pydantic import ValidationError
from pathlib import Path

from app.domain.llm_contracts import LLMInput, LLMOutput
from app.services.analysis.prompts import ANALYSIS_PROMPT_V1
from app.core.config import settings
from app.core.usage_tracker import increment_ai_calls

logger = logging.getLogger(__name__)

# genai.configure no longer used in new SDK, using Client(api_key=...)

MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds


def run_llm_analysis_from_file(file_path: str, platform: str, db, user_id) -> LLMOutput:
    """
    Send the file directly to the LLM for analysis.
    This is simpler and more powerful than parsing first.
    """
    try:
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
        
        # Truncate if too large (max ~30KB for context)
        # if len(file_content) > 30000:
        #     file_content = file_content[:30000] + "\n... (truncated)"
        
        prompt = f"""You are an expert RPA workflow analyst.

Analyze this {platform} workflow file and provide insights.

Workflow Content:
```
{file_content}
```

Provide a JSON response with:
{{
  "summary": "Brief overview of what this workflow does",
  "risks": ["Risk 1", "Risk 2"],
  "optimization_suggestions": ["Suggestion 1", "Suggestion 2"],
  "migration_notes": ["Note 1", "Note 2"]
}}
"""
        
        client = genai.Client(api_key=settings.google_api_key)
        
        increment_ai_calls(db, user_id)
        
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt,
            config={
                "temperature": 0.3,
                "max_output_tokens": 1024,
                "response_mime_type": "application/json"
            },
        )
        
        raw_text = response.text.strip()
        logger.info(f"LLM direct file analysis response: {raw_text[:200]}...")
        
        # Clean up response
        cleaned_text = raw_text
        if cleaned_text.startswith("```"):
            cleaned_text = re.sub(r'^```(?:json)?\s*', '', cleaned_text)
            cleaned_text = re.sub(r'\s*```$', '', cleaned_text)
            cleaned_text = cleaned_text.strip()
        
        parsed = json.loads(cleaned_text)
        
        return LLMOutput(
            summary=parsed.get("summary", "Analysis completed"),
            risks=parsed.get("risks", []),
            optimization_suggestions=parsed.get("optimization_suggestions", []),
            migration_notes=parsed.get("migration_notes", []),
        )
        
    except Exception as e:
        logger.error(f"Direct file analysis failed: {str(e)}")
        # Fallback to empty result
        return LLMOutput(
            summary="Unable to analyze file directly. Please try again.",
            risks=[],
            optimization_suggestions=[],
            migration_notes=[],
        )


def run_llm_analysis(data: LLMInput, db, user_id, file_path: str = None) -> LLMOutput:
    file_content_section = ""
    if file_path and Path(file_path).exists():
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                file_content_section = f"\n\nRaw Workflow Content:\n```\n{content}\n```"
        except Exception as e:
            logger.warning(f"Failed to read file for LLM analysis: {str(e)}")

    prompt = ANALYSIS_PROMPT_V1.format(
        platform=data.platform,
        activity_count=data.metrics.activity_count,
        variable_count=data.metrics.variable_count,
        nesting_depth=data.metrics.nesting_depth,
        invoked_workflows=data.metrics.invoked_workflows,
        has_custom_code=data.metrics.has_custom_code,
    ) + file_content_section

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
                    "response_mime_type": "application/json"
                },
            )

            raw_text = response.text.strip()
            logger.info(f"LLM raw response (attempt {attempt}): {raw_text[:200]}...")
            
            # Clean up the response - remove markdown code blocks if present
            cleaned_text = raw_text
            if cleaned_text.startswith("```"):
                # Remove ```json or ``` at start and ``` at end
                cleaned_text = re.sub(r'^```(?:json)?\s*', '', cleaned_text)
                cleaned_text = re.sub(r'\s*```$', '', cleaned_text)
                cleaned_text = cleaned_text.strip()
            
            parsed = json.loads(cleaned_text)
            logger.info(f"Successfully parsed LLM response on attempt {attempt}")

            return LLMOutput(
                summary=parsed.get("summary", "Analysis completed"),
                risks=parsed.get("risks", []),
                optimization_suggestions=parsed.get("optimization_suggestions", []),
                migration_notes=parsed.get("migration_notes", []),
            )

        except (json.JSONDecodeError, KeyError, ValidationError) as e:
            last_error = e
            logger.warning(f"LLM parsing error on attempt {attempt}: {str(e)}")
        except Exception as e:
            last_error = e
            logger.error(f"Unexpected error on attempt {attempt}: {str(e)}")

        if attempt < MAX_RETRIES:
            time.sleep(RETRY_DELAY)

    # Final fallback (never crash analysis)
    logger.error(f"All LLM attempts failed. Last error: {last_error}")
    return LLMOutput(
        summary="AI analysis temporarily unavailable. Please try again.",
        risks=[],
        optimization_suggestions=[],
        migration_notes=[],
    )
