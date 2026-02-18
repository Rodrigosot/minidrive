from fastapi import APIRouter

router = APIRouter(tags=["Health"])

@router.get("/health", summary="Health Check Endpoint")
def health_check():
    return {"status": "ok"}