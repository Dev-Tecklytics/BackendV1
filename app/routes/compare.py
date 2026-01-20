from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/compare", tags=["Compare"])


@router.post("")
def compare(activity_count: int, mapped_activities: int):
    from app.services.comparison.engine import compare_workflow
    return compare_workflow(activity_count, mapped_activities)
