from sqlalchemy import Column, Integer, ForeignKey, DateTime, UUID
import uuid
from datetime import datetime
from app.core.database import Base

class FileShare(Base):
    __tablename__ = "fileshares"
    id = Column(UUID(as_uuid=True), primary_key=True, unique=True, default=uuid.uuid4, nullable=False)
    file_id = Column(UUID(as_uuid=True), ForeignKey("files.id"), nullable=False)
    shared_with_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True) # Null = compartido públicamente
    shared_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)  # Null = sin expiración
    created_at = Column(DateTime, default=datetime.utcnow)
    
