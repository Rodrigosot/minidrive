from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, UUID
from datetime import datetime
import uuid
from app.core.database import Base

class ActivityLog(Base):
    __tablename__ = "activitylogs"

    id = Column(UUID(as_uuid=True), primary_key=True, unique=True, default=uuid.uuid4, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    action = Column(String, nullable=False) # Descripción de la acción realizada
    target_type = Column(String, nullable=True) # Tipo de entidad afectada (e.g., 'file', 'folder')
    target_id = Column(UUID(as_uuid=True), nullable=True) # ID de la entidad afectada
    details = Column(String, nullable=True) # Detalles adicionales sobre la acción
    created_at = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String, nullable=True) # Dirección IP desde donde se realizó la acción