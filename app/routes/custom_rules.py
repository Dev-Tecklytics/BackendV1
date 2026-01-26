from fastapi import APIRouter, Depends, HTTPException, Response, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel
import json
import io
from datetime import datetime

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.custom_rules import CustomRule
from app.models.user import User
from app.services.custom_rules.engine import run_custom_rules

router = APIRouter(prefix="/api/v1/custom-rules", tags=["Custom Rules"])


class CustomRuleCreate(BaseModel):
    name: str
    rule_type: str  # regex | activity_count | nesting_depth
    config: dict
    severity: str  # low | medium | high | critical
    is_active: Optional[bool] = True


class CustomRuleUpdate(BaseModel):
    ruleName: Optional[str] = None
    category: Optional[str] = None
    severity: Optional[str] = None
    platform: Optional[str] = None
    description: Optional[str] = None
    recommendation: Optional[str] = None
    checkType: Optional[str] = None
    checkPattern: Optional[str] = None
    checkConfig: Optional[dict] = None
    isActive: Optional[bool] = None
    isShared: Optional[bool] = None


class BulkUpdateRequest(BaseModel):
    ruleIds: List[str]
    action: str  # activate, deactivate, delete, updateField
    value: Optional[dict] = None


class ImportRequest(BaseModel):
    rules: List[dict]
    overwrite: Optional[bool] = False


@router.post("")
def create_custom_rule(
    rule_data: CustomRuleCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Create a new custom rule for the authenticated user."""
    
    # Validate rule_type
    valid_types = ["regex", "activity_count", "nesting_depth"]
    if rule_data.rule_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid rule_type. Must be one of: {', '.join(valid_types)}"
        )
    
    # Validate severity
    valid_severities = ["low", "medium", "high", "critical"]
    if rule_data.severity not in valid_severities:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid severity. Must be one of: {', '.join(valid_severities)}"
        )
    
    # Create the custom rule
    custom_rule = CustomRule(
        user_id=user.user_id,
        name=rule_data.name,
        rule_type=rule_data.rule_type,
        config=rule_data.config,
        severity=rule_data.severity,
        is_active=rule_data.is_active,
    )
    
    db.add(custom_rule)
    db.commit()
    db.refresh(custom_rule)
    
    return {
        "rule_id": str(custom_rule.rule_id),
        "user_id": str(custom_rule.user_id),
        "name": custom_rule.name,
        "rule_type": custom_rule.rule_type,
        "config": custom_rule.config,
        "severity": custom_rule.severity,
        "is_active": custom_rule.is_active,
        "created_at": custom_rule.created_at.isoformat() if custom_rule.created_at else None,
    }


@router.get("/{rule_id}")
def get_custom_rule(
    rule_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get a specific custom rule by ID."""
    rule = db.query(CustomRule).filter(
        CustomRule.rule_id == rule_id,
        CustomRule.user_id == user.user_id
    ).first()
    
    if not rule:
        raise HTTPException(status_code=404, detail="Custom rule not found")
    
    return {
        "rule_id": str(rule.rule_id),
        "user_id": str(rule.user_id),
        "name": rule.name,
        "rule_type": rule.rule_type,
        "config": rule.config,
        "severity": rule.severity,
        "is_active": rule.is_active,
        "created_at": rule.created_at.isoformat() if rule.created_at else None,
    }


@router.get("")
def list_custom_rules(
    rule_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List all custom rules for the authenticated user with optional filtering."""
    query = db.query(CustomRule).filter(CustomRule.user_id == user.user_id)
    
    if rule_type:
        query = query.filter(CustomRule.rule_type == rule_type)
    
    if is_active is not None:
        query = query.filter(CustomRule.is_active == is_active)
    
    total = query.count()
    rules = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "rules": [
            {
                "rule_id": str(r.rule_id),
                "user_id": str(r.user_id),
                "name": r.name,
                "rule_type": r.rule_type,
                "config": r.config,
                "severity": r.severity,
                "is_active": r.is_active,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in rules
        ]
    }


@router.patch("/{rule_id}")
def update_custom_rule_patch(
    rule_id: UUID,
    update_data: CustomRuleUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Update a custom rule (PATCH method)."""
    rule = db.query(CustomRule).filter(
        CustomRule.rule_id == rule_id,
        CustomRule.user_id == user.user_id
    ).first()
    
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    # Validate severity if provided
    if update_data.severity:
        valid_severities = ["critical", "major", "minor", "info", "Critical", "Major", "Minor", "Info"]
        if update_data.severity not in valid_severities:
            raise HTTPException(status_code=400, detail="Invalid severity")
    
    # Validate platform if provided
    if update_data.platform:
        valid_platforms = ["UiPath", "BluePrism", "Both"]
        if update_data.platform not in valid_platforms:
            raise HTTPException(status_code=400, detail="Invalid platform")
    
    # Update fields
    update_dict = update_data.dict(exclude_unset=True)
    for field, value in update_dict.items():
        if hasattr(rule, field):
            setattr(rule, field, value)
    
    db.commit()
    db.refresh(rule)
    
    return {
        "message": "Rule updated successfully",
        "rule": rule
    }


@router.patch("/bulk")
def bulk_update_rules(
    request_data: BulkUpdateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Bulk update custom rules."""
    if not request_data.ruleIds:
        raise HTTPException(status_code=400, detail="ruleIds array is required")
    
    # Convert string IDs to UUIDs
    try:
        rule_uuids = [UUID(rule_id) for rule_id in request_data.ruleIds]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid rule ID format")
    
    # Verify rules belong to user
    existing_rules = db.query(CustomRule).filter(
        CustomRule.rule_id.in_(rule_uuids),
        CustomRule.user_id == user.user_id
    ).all()
    
    if len(existing_rules) != len(rule_uuids):
        raise HTTPException(
            status_code=404,
            detail="Some rules not found or do not belong to you"
        )
    
    affected = 0
    
    if request_data.action == "activate":
        for rule in existing_rules:
            rule.is_active = True
        affected = len(existing_rules)
    elif request_data.action == "deactivate":
        for rule in existing_rules:
            rule.is_active = False
        affected = len(existing_rules)
    elif request_data.action == "delete":
        for rule in existing_rules:
            db.delete(rule)
        affected = len(existing_rules)
    elif request_data.action == "updateField":
        if not request_data.value:
            raise HTTPException(
                status_code=400,
                detail="value object is required for updateField action"
            )
        for rule in existing_rules:
            for field, value in request_data.value.items():
                if hasattr(rule, field):
                    setattr(rule, field, value)
        affected = len(existing_rules)
    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid action. Must be: activate, deactivate, delete, or updateField"
        )
    
    db.commit()
    
    return {
        "message": f"Bulk {request_data.action} completed successfully",
        "affected": affected
    }


@router.get("/export/{file_format}")
def export_rules(
    file_format: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Export custom rules as JSON or CSV."""
    query = db.query(CustomRule).filter(CustomRule.user_id == user.user_id)
    
    # if platform and platform != "all":
    #     query = query.filter(CustomRule.platform == platform)
    
    # if category and category != "all":
    #     query = query.filter(CustomRule.category == category)
    
    # if isActive is not None:
    #     query = query.filter(CustomRule.is_active == isActive)
    
    rules = query.order_by(
        CustomRule.category,
        CustomRule.severity,
        CustomRule.name
    ).all()
    
    if file_format == "csv":
        # Generate CSV
        headers = [
            "Rule ID", "Rule Name", "Category", "Severity", "Platform",
            "Description", "Recommendation", "Check Type", "Check Pattern",
            "Is Active", "Is Shared"
        ]
        
        csv_data = []
        csv_data.append(",".join(headers))
        
        for rule in rules:
            row = [
                str(rule.rule_id),
                f'"{rule.name.replace('"', '""')}"',
                rule.category or "",
                rule.severity or "",
                rule.platform or "",
                f'"{(rule.description or "").replace('"', '""')}"',
                f'"{(rule.recommendation or "").replace('"', '""')}"',
                rule.rule_type or "",
                f'"{str(rule.config or "").replace('"', '""')}"',
                str(rule.is_active),
                "false"  # isShared equivalent
            ]
            csv_data.append(",".join(row))
        
        csv_content = "\n".join(csv_data)
        
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=custom-rules-{int(datetime.now().timestamp())}.csv"
            }
        )
    
    # JSON format
    export_data = {
        "exportedAt": datetime.now().isoformat(),
        "totalRules": len(rules),
        "platform":  "all",
        "category":  "all",
        "rules": [
            {
                "ruleId": str(rule.rule_id),
                "ruleName": rule.name,
                "category": rule.category,
                "severity": rule.severity,
                "platform": rule.platform,
                "description": rule.description,
                "recommendation": rule.recommendation,
                "checkType": rule.rule_type,
                "checkPattern": str(rule.config) if rule.config else None,
                "checkConfig": rule.config,
                "isActive": rule.is_active,
                "isShared": False
            }
            for rule in rules
        ]
    }
    
    return Response(
        content=json.dumps(export_data, indent=2),
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename=custom-rules-{int(datetime.now().timestamp())}.json"
        }
    )


@router.post("/import")
def import_rules(
    request_data: ImportRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Import custom rules from JSON array."""
    if not request_data.rules:
        raise HTTPException(
            status_code=400,
            detail="Invalid import format. Expected array of rules"
        )
    
    # Validation constants
    valid_severities = ["Critical", "Major", "Minor", "Info"]
    valid_platforms = ["UiPath", "BluePrism", "Both"]
    valid_check_types = ["regex", "activity_count", "nesting_depth", "custom"]
    
    # Validate rules
    validated_rules = []
    errors = []
    
    for i, rule in enumerate(request_data.rules):
        rule_errors = []
        
        # Check required fields
        if not rule.get("ruleName"):
            rule_errors.append("ruleName is required")
        if not rule.get("category"):
            rule_errors.append("category is required")
        if not rule.get("severity"):
            rule_errors.append("severity is required")
        if not rule.get("platform"):
            rule_errors.append("platform is required")
        if not rule.get("description"):
            rule_errors.append("description is required")
        if not rule.get("checkType"):
            rule_errors.append("checkType is required")
        
        # Validate enums
        if rule.get("severity") and rule["severity"] not in valid_severities:
            rule_errors.append(f"Invalid severity: {rule['severity']}")
        if rule.get("platform") and rule["platform"] not in valid_platforms:
            rule_errors.append(f"Invalid platform: {rule['platform']}")
        if rule.get("checkType") and rule["checkType"] not in valid_check_types:
            rule_errors.append(f"Invalid checkType: {rule['checkType']}")
        
        if rule_errors:
            errors.append({
                "index": i,
                "ruleName": rule.get("ruleName", "Unknown"),
                "errors": rule_errors
            })
        else:
            validated_rules.append(rule)
    
    if errors:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Validation failed for some rules",
                "validationErrors": errors,
                "validCount": len(validated_rules),
                "errorCount": len(errors)
            }
        )
    
    # Check for existing rules
    rule_names = [r["ruleName"] for r in validated_rules]
    existing_rules = db.query(CustomRule).filter(
        CustomRule.user_id == user.user_id,
        CustomRule.name.in_(rule_names)
    ).all()
    
    existing_names = {r.name for r in existing_rules}
    
    # Handle overwrite
    if request_data.overwrite and existing_names:
        for rule in existing_rules:
            db.delete(rule)
        db.commit()
    
    rules_to_import = (
        validated_rules if request_data.overwrite
        else [r for r in validated_rules if r["ruleName"] not in existing_names]
    )
    
    # Import rules
    imported_rules = []
    for rule in rules_to_import:
        new_rule = CustomRule(
            user_id=user.user_id,
            name=rule["ruleName"],
            category=rule["category"],
            severity=rule["severity"],
            platform=rule["platform"],
            description=rule["description"],
            recommendation=rule.get("recommendation", "Please review and fix this issue"),
            rule_type=rule["checkType"],
            config=rule.get("checkConfig"),
            is_active=rule.get("isActive", True)
        )
        db.add(new_rule)
        imported_rules.append(new_rule)
    
    db.commit()
    
    return {
        "message": f"Successfully imported {len(imported_rules)} rules",
        "imported": len(imported_rules),
        "skipped": len(validated_rules) - len(rules_to_import),
        "overwritten": len(existing_names) if request_data.overwrite else 0,
        "rules": [str(r.rule_id) for r in imported_rules]
    }


@router.delete("/{rule_id}")
def delete_custom_rule(
    rule_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Delete a custom rule."""
    rule = db.query(CustomRule).filter(
        CustomRule.rule_id == rule_id,
        CustomRule.user_id == user.user_id
    ).first()
    
    if not rule:
        raise HTTPException(status_code=404, detail="Custom rule not found")
    
    db.delete(rule)
    db.commit()
    
    return {
        "message": "Custom rule deleted successfully",
        "rule_id": str(rule_id)
    }


@router.post("/validate")
def validate_workflow_with_custom_rules(
    workflow_metrics: dict,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Validate workflow metrics against user's active custom rules.
    
    Expected workflow_metrics format:
    {
        "activity_count": 25,
        "nesting_depth": 3,
        "variable_count": 10
    }
    """
    # Get all active custom rules for the user
    active_rules = db.query(CustomRule).filter(
        CustomRule.user_id == user.user_id,
        CustomRule.is_active == True
    ).all()
    
    if not active_rules:
        return {
            "findings": [],
            "total_violations": 0,
            "message": "No active custom rules found"
        }
    
    # Run custom rules validation
    findings = run_custom_rules(active_rules, workflow_metrics)
    
    return {
        "findings": findings,
        "total_violations": len(findings),
        "rules_checked": len(active_rules)
    }
