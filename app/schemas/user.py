from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
import uuid


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Nombre de usuario")
    email: EmailStr
    password: str = Field(..., min_length=6, description="Contraseña del usuario")

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserResponse(BaseModel):
    id: uuid.UUID
    username: str
    email: str
    role_id: uuid.UUID
    is_active: bool

    class Config:
        orm_mode = True
