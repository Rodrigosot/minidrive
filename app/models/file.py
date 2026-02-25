from sqlalchemy import Boolean, String, Integer, ForeignKey, DateTime, UUID
from sqlalchemy.orm import Mapped, mapped_column
import uuid
from datetime import datetime
from app.core.database import Base


class File(Base):
    __tablename__ = "files"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )


    folder_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("folders.id"),
        nullable=False
    )

    name: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    path: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    size: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    mime_type: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    hash: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    
    deleted_at : Mapped[datetime] = mapped_column(
        DateTime, 
        nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
