from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session
from app.core.limiter import limiter
from app.core.database import get_db
from app.models.plan import Plan
from app.models.user_plan import UserPlan
from app.models.user import User
from app.models.role import Role
from app.schemas.user import UserCreate, UserLogin
from app.core.security import hash_password, verify_password
from app.core.security import create_access_token, create_refresh_token, refresh_token
import uuid
from datetime import datetime

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/")
@limiter.limit("5/minute")
def create_user(request: Request ,user: UserCreate, response:Response, db: Session = Depends(get_db)):
    
    # Buscar rol "user"
    existing_user = db.query(User).filter(User.email == user.email).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    role = db.query(Role).filter(Role.name == "user").first()
    free_plan = db.query(Plan).filter(Plan.name == "Gratis").first()

    
    new_user = User(
        id=uuid.uuid4(),
        role_id=role.id,
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password),  
        created_at=datetime.utcnow()
    )

    user_plan = UserPlan(
        user_id=new_user.id,
        plan_id=free_plan.id,
        storage_used=0,
        active=True,
        started_at=datetime.utcnow(),
        expires_at= None
    )

    db.add(new_user)
    db.add(user_plan)
    db.commit()
    db.refresh(new_user)

    access_token = create_access_token({"sub": str(new_user.id)})
    refresh_token = create_refresh_token({"sub": str(new_user.id)})

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

@router.post("/login")
@limiter.limit("5/minute")
def login(request: Request, res:Response, user: UserLogin, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()

    if not existing_user or not verify_password(user.password, existing_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token({"sub": str(existing_user.id)})
    refresh_token = create_refresh_token({"sub": str(existing_user.id)})
    res.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

@router.post("/refresh")
def refresh(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("refresh_token")

    if not token:
        raise HTTPException(status_code=401, detail="Refresh token not found")

    new_access_token = refresh_token(token, db)
    return {"access_token": new_access_token, "token_type": "bearer"}

@router.post("/logout") 
def logout(response: Response):
    response.delete_cookie(key="refresh_token")
    return {"message": "Logged out successfully"}