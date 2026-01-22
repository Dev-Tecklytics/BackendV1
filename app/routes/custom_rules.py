from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel

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
    name: Optional[str] = None
    rule_type: Optional[str] = None
    config: Optional[dict] = None
    severity: Optional[str] = None
    is_active: Optional[bool] = None


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


@router.put("/{rule_id}")
def update_custom_rule(
    rule_id: UUID,
    update_data: CustomRuleUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Update a custom rule."""
    rule = db.query(CustomRule).filter(
        CustomRule.rule_id == rule_id,
        CustomRule.user_id == user.user_id
    ).first()
    
    if not rule:
        raise HTTPException(status_code=404, detail="Custom rule not found")
    
    # Validate rule_type if provided
    if update_data.rule_type:
        valid_types = ["regex", "activity_count", "nesting_depth"]
        if update_data.rule_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid rule_type. Must be one of: {', '.join(valid_types)}"
            )
    
    # Validate severity if provided
    if update_data.severity:
        valid_severities = ["low", "medium", "high", "critical"]
        if update_data.severity not in valid_severities:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid severity. Must be one of: {', '.join(valid_severities)}"
            )
    
    # Update only provided fields
    update_dict = update_data.dict(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(rule, field, value)
    
    db.commit()
    db.refresh(rule)
    
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
