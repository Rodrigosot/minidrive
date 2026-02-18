from pydantic import BaseModel
import uuid

class FolderCreate(BaseModel):
    name: str

class FolderRename(BaseModel):
    id : uuid.UUID
    name: str
