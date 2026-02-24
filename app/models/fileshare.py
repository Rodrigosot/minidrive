from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, DateTime, UUID
from typing import Optional
import uuid
from datetime import datetime
from app.core.database import Base

class FileShare(Base):
    __tablename__ = "fileshares"

    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
    )

    file_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("files.id"),
        nullable=False,
    )

    shared_with_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        unique=True,
        default=uuid.uuid4,
        nullable=False,
        
    )

    shared_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )