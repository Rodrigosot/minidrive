from sqlalchemy import Column, Integer, ForeignKey, DateTime, UUID
import uuid
from datetime import datetime
from app.core.database import Base

class UserPlanHistory(Base):
    __tablename__ = "user_plan_histories"

    id = Column(UUID(as_uuid=True), primary_key=True, unique=True, default=uuid.uuid4, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id"), nullable=False)
    storage_used = Column(Integer, default=0)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=False)
    
