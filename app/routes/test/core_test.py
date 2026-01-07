import time
from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session
from app.core.core_context import get_core_context
from app.core.usage_tracker import track_usage
from app.core.deps import get_db

router = APIRouter(
    prefix="/api/v1/core",
    tags=["Core APIs"]
)

@router.get("/test")
def core_test(
    request: Request,
    response: Response,
    context=Depends(get_core_context),
    db: Session = Depends(get_db)
):
    start_time = time.time()

    # ---- Business logic ----
    result = {
        "message": "Access granted",
        "user_email": context["user"].email,
        "subscription_status": context["subscription"].status.value
    }

    # ---- Track usage ----
    track_usage(
        request=request,
        context=context,
        db=db,
        response_status=response.status_code,
        start_time=start_time
    )

    return result
