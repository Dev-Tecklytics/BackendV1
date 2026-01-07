from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.admin_auth import require_admin
from app.models.subscription import Subscription
from app.models.user import User
from app.models.subscription_plan import SubscriptionPlan
from app.schemas.admin import AdminSubscriptionResponse

router = APIRouter(
    prefix="/api/v1/admin",
    tags=["Admin APIs"]
)

@router.get("/subscriptions", response_model=list[AdminSubscriptionResponse])
def list_subscriptions(
    db: Session = Depends(get_db),
    admin_user = Depends(require_admin)
):
    results = (
        db.query(
            Subscription.subscription_id,
            User.email.label("user_email"),
            SubscriptionPlan.name.label("plan_name"),
            Subscription.status,
            Subscription.start_date,
            Subscription.end_date
        )
        .join(User, Subscription.user_id == User.user_id)
        .join(SubscriptionPlan, Subscription.plan_id == SubscriptionPlan.plan_id)
        .order_by(Subscription.start_date.desc())
        .all()
    )

    return results
