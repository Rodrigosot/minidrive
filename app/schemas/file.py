import uuid

from pydantic import BaseModel

class FileRename(BaseModel):
    id: uuid.UUID
    name: str