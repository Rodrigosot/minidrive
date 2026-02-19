from fastapi import FastAPI
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
from app.api.V1.health import router as health_router
from app.api.V1.users import router as user_router
from app.api.V1.auth import router as auth_router
from app.api.V1.folder import router as folder_router
from app.api.V1.file import router as file_router
from app.core.config import settings

app = FastAPI(title=settings.APP_NAME, version=settings.VERSION)
app.state.limiter = Limiter

@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please try again later."}
    )

app.include_router(health_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(folder_router, prefix="/api/v1")
app.include_router(file_router, prefix="/api/v1")