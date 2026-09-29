from fastapi import APIRouter, HTTPException

from services.dashboard_service import get_dashboard


router = APIRouter(
    prefix="/api",
    tags=["Dashboard"],
)


@router.get("/dashboard")
def dashboard():
    try:
        return get_dashboard()
    except Exception as error:
        print("Dashboard error:", repr(error))
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )
