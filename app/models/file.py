from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, UUID
import uuid
from datetime import datetime
from app.core.database import Base

class File(Base):
    __tablename__ = "files"
    id = Column(UUID(as_uuid=True), primary_key=True, unique=True, default=uuid.uuid4, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    folder_id = Column(UUID(as_uuid=True), ForeignKey("folders.id"), nullable=False)
    name = Column(String, nullable=False)
    path = Column(String, nullable=False) # Ruta en disco
    size = Column(Integer, nullable=False) # Tamaño en bytes
    mime_type = Column(String, nullable=False) # Tipo MIME
    hash = Column(String, nullable=False) # Hash para integridad
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
