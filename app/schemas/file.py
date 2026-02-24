from typing import Optional
import uuid

from pydantic import BaseModel, EmailStr

class FileRename(BaseModel):
    id: uuid.UUID
    name: str

class ShareFileSchema(BaseModel):
    email: EmailStr  
    expires_in_days: Optional[int] = 0
    expires_in_hours: Optional[int] = 0
    expires_in_minutes: Optional[int] = 0
    forever: Optional[bool] = False

