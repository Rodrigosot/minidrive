from sqlalchemy import String, ForeignKey, DateTime, UUID
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
import uuid
from app.core.database import Base


class ActivityLog(Base):
    __tablename__ = "activitylogs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )

    action: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    # Tipo de entidad afectada (ej: 'file', 'folder')
    target_type: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )

    # ID de la entidad afectada
    target_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True
    )

    # Detalles adicionales
    details: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    ip_address: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )