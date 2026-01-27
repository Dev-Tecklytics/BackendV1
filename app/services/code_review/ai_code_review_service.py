
import json
import time
from typing import Dict, List, Any
from google import genai
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.usage_tracker import increment_ai_calls


# Pydantic models for type safety and validation
class AIInsightModel(BaseModel):
    category: str
    severity: str
    title: str
    description: str
    recommendation: str
    reasoning: str
    confidence: float = Field(ge=0.0, le=1.0)
    related_activities: List[str] = []


class AICodeReviewResult(BaseModel):
    overall_assessment: str
    insights: List[AIInsightModel]
    patterns: Dict[str, List[str]]  # {identified: [], antiPatterns: []}
    optimization_opportunities: List[str]
    migration_risks: List[str]
    estimated_impact: Dict[str, int]  # {maintainability, performance, reliability}


# Constants
MAX_RETRIES = 3
RETRY_DELAY = 2 
MODEL_NAME = "gemini-2.5-flash" 


def build_analysis_prompt(input_data: Dict[str, Any]) -> str:
    workflow = input_data.get("workflow", {})
    platform = input_data.get("platform", "Unknown")
    rule_findings_count = input_data.get("ruleFindingsCount", 0)
    complexity = input_data.get("complexity", "Unknown")
    
    # Build activity breakdown text
    activity_breakdown = workflow.get("activityBreakdown", {})
    breakdown_text = "\n".join([f"  - {k}: {v}" for k, v in activity_breakdown.items()])
    
    # Build variables text
    variables = workflow.get("variables", [])
    variables_text = "\n".join([
        f"  - {v.get('name', 'Unknown')} ({v.get('variableType', 'Unknown')})"
        for v in variables[:10]  # Limit to first 10 to avoid token overflow
    ])
    if len(variables) > 10:
        variables_text += f"\n  ... and {len(variables) - 10} more"
    
    # Build invoked workflows text
    invoked_workflows = workflow.get("invokedWorkflows", [])
    invoked_text = "\n".join([f"  - {w}" for w in invoked_workflows[:5]])
    if len(invoked_workflows) > 5:
        invoked_text += f"\n  ... and {len(invoked_workflows) - 5} more"
    
    prompt = f"""You are an expert RPA code reviewer with deep knowledge of {platform} best practices, design patterns, and common pitfalls.

**Workflow Overview:**
- Name: {workflow.get('workflowName', 'Unknown')}
- Platform: {platform}
- Complexity: {complexity}
- Total Activities: {workflow.get('totalActivities', 0)}
- Nesting Depth: {workflow.get('nestingDepth', 0)}
- Variables: {workflow.get('variableCount', 0)}
- Arguments: {workflow.get('argumentCount', 0)}
- Invoked Workflows: {workflow.get('invokedWorkflowCount', 0)}
- Has Custom Code: {workflow.get('hasCustomCode', False)}
- Exception Handlers: {workflow.get('exceptionHandlers', 0)}
- Rule-based Findings: {rule_findings_count}

**Activity Breakdown:**
{breakdown_text if breakdown_text else "  No breakdown available"}

**Variables (Sample):**
{variables_text if variables_text else "  No variables"}

**Invoked Workflows:**
{invoked_text if invoked_text else "  None"}

**Your Task:**
Perform a comprehensive code review focusing on:
1. **Architecture & Design Patterns**: Identify good patterns and anti-patterns
2. **Performance**: Potential bottlenecks and optimization opportunities
3. **Maintainability**: Code organization, naming conventions, reusability
4. **Error Handling**: Exception handling completeness and robustness
5. **Security**: Credential management, data exposure risks
6. **Best Practices**: Platform-specific recommendations

**IMPORTANT**: You MUST respond with ONLY valid JSON in this EXACT format:

{{
  "overall_assessment": "A comprehensive 2-3 sentence summary of the workflow's quality and main concerns",
  "insights": [
    {{
      "category": "Architecture|Performance|Maintainability|ErrorHandling|Security|BestPractices",
      "severity": "Critical|Major|Minor|Info",
      "title": "Short descriptive title",
      "description": "Detailed description of the finding",
      "recommendation": "Specific actionable recommendation",
      "reasoning": "Why this matters and the impact",
      "confidence": 0.85,
      "related_activities": ["Activity1", "Activity2"]
    }}
  ],
  "patterns": {{
    "identified": ["Good pattern 1", "Good pattern 2"],
    "antiPatterns": ["Anti-pattern 1", "Anti-pattern 2"]
  }},
  "optimization_opportunities": [
    "Specific optimization opportunity 1",
    "Specific optimization opportunity 2"
  ],
  "migration_risks": [
    "Migration risk 1 (if applicable)",
    "Migration risk 2 (if applicable)"
  ],
  "estimated_impact": {{
    "maintainability": 75,
    "performance": 80,
    "reliability": 85
  }}
}}

Provide at least 3-5 insights covering different categories. Be specific and actionable.
"""
    
    return prompt


def normalize_ai_response(raw_response: Dict[str, Any]) -> AICodeReviewResult:
    """
    Normalize and validate AI response to ensure consistency.
    
    Args:
        raw_response: Raw JSON response from AI
        
    Returns:
        Validated AICodeReviewResult
    """
    # Ensure all required fields exist with defaults
    normalized = {
        "overall_assessment": raw_response.get("overall_assessment", "Analysis completed"),
        "insights": [],
        "patterns": {
            "identified": raw_response.get("patterns", {}).get("identified", []),
            "antiPatterns": raw_response.get("patterns", {}).get("antiPatterns", [])
        },
        "optimization_opportunities": raw_response.get("optimization_opportunities", []),
        "migration_risks": raw_response.get("migration_risks", []),
        "estimated_impact": {
            "maintainability": raw_response.get("estimated_impact", {}).get("maintainability", 70),
            "performance": raw_response.get("estimated_impact", {}).get("performance", 70),
            "reliability": raw_response.get("estimated_impact", {}).get("reliability", 70)
        }
    }
    
    # Normalize insights
    for insight in raw_response.get("insights", []):
        normalized_insight = {
            "category": insight.get("category", "General"),
            "severity": insight.get("severity", "Info"),
            "title": insight.get("title", "Insight"),
            "description": insight.get("description", ""),
            "recommendation": insight.get("recommendation", ""),
            "reasoning": insight.get("reasoning", ""),
            "confidence": float(insight.get("confidence", 0.7)),
            "related_activities": insight.get("related_activities", [])
        }
        normalized["insights"].append(normalized_insight)
    
    # Validate with Pydantic
    return AICodeReviewResult(**normalized)


async def perform_ai_code_review(
    input_data: Dict[str, Any],
    db,
    user_id: str
) -> AICodeReviewResult:
    prompt = build_analysis_prompt(input_data)
    
    # Initialize Gemini client
    client = genai.Client(api_key=settings.google_api_key)
    
    last_error = None
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            # Track AI usage
            increment_ai_calls(db, user_id)
            
            # Call Gemini API
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config={
                    "temperature": 0.3,  # Lower temperature for more consistent results
                    "max_output_tokens": 4000,  # Increased for comprehensive analysis
                    "response_mime_type": "application/json",  # Force JSON response
                }
            )
            
            # Parse response
            raw_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.startswith("```"):
                raw_text = raw_text[3:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
            
            raw_text = raw_text.strip()
            
            # Parse JSON
            parsed = json.loads(raw_text)
            
            # Normalize and validate
            result = normalize_ai_response(parsed)
            
            return result
            
        except json.JSONDecodeError as e:
            last_error = f"JSON parsing error: {str(e)}"
            print(f"Attempt {attempt}/{MAX_RETRIES} failed: {last_error}")
            
        except Exception as e:
            last_error = f"AI analysis error: {str(e)}"
            print(f"Attempt {attempt}/{MAX_RETRIES} failed: {last_error}")
        
        # Wait before retry (except on last attempt)
        if attempt < MAX_RETRIES:
            time.sleep(RETRY_DELAY)
    
    # If all retries failed, raise exception
    raise Exception(f"AI code review failed after {MAX_RETRIES} attempts. Last error: {last_error}")


def perform_ai_code_review_sync(
    input_data: Dict[str, Any],
    db,
    user_id: str
) -> AICodeReviewResult:
    import asyncio
    
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(perform_ai_code_review(input_data, db, user_id))
