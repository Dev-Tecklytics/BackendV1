from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.core.auth import get_current_user
from app.models.subscription import Subscription
from app.models.subscription_plan import SubscriptionPlan

router = APIRouter(
    prefix="/api/v1/subscription",
    tags=["Subscription"]
)

@router.get("/plans")
def list_plans(db: Session = Depends(get_db)):
    return db.query(SubscriptionPlan).filter(
        SubscriptionPlan.is_active == True
    ).all()

@router.post("/subscribe")
def subscribe(
    plan_id: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sub = Subscription(
        user_id=current_user.user_id,
        plan_id=plan_id,
        status="active"
    )
    db.add(sub)
    db.commit()
    return {"message": "Subscribed"}

@router.get("/current")
def current_subscription(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Subscription).filter(
        Subscription.user_id == current_user.user_id
    ).first()

@router.put("/upgrade")
def upgrade_subscription():
    return {"message": "Subscription upgraded"}

@router.post("/cancel")
def cancel_subscription():
    return {"message": "Subscription cancelled"}

@router.get("/usage")
def subscription_usage():
    return {"usage": "Usage details placeholder"}
