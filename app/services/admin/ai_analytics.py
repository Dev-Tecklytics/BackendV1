from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.usage_tracking import UsageTracking


def get_ai_usage_summary(db: Session):
    return db.query(
        func.sum(UsageTracking.ai_calls_count).label("total_ai_calls"),
        func.avg(UsageTracking.ai_calls_count).label("avg_ai_calls"),
    ).one()


def get_top_ai_users(db: Session, limit: int = 10):
    return (
        db.query(
            UsageTracking.user_id,
            UsageTracking.ai_calls_count,
        )
        .order_by(UsageTracking.ai_calls_count.desc())
        .limit(limit)
        .all()
    )
 