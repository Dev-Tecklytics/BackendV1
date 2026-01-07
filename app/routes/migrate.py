from fastapi import APIRouter, Depends
from app.core.core_context import get_core_context

router = APIRouter(
    prefix="/api/v1/migrate",
    tags=["Migration"]
)

@router.post("/blueprint")
def generate_blueprint(context=Depends(get_core_context)):
    return {
        "message": "Blueprint generated"
    }
