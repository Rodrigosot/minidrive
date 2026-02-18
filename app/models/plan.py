from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, UUID
import uuid
from datetime import datetime
from app.core.database import Base

class Plan(Base):
    __tablename__ = "plans"
    id = Column(UUID(as_uuid=True), primary_key=True, unique=True, default=uuid.uuid4, nullable=False)
    name = Column(String, unique=True, index=True, nullable=False)
    storage_limit = Column(Integer, nullable=False)
    price_per_month = Column(Integer, nullable=False)
    
