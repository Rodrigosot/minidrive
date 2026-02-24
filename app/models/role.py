from sqlalchemy import String, DateTime, UUID
from sqlalchemy.orm import Mapped, mapped_column
import uuid
from datetime import datetime
from app.core.database import Base


class Role(Base):
    __tablename__ = "roles"


    name: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )


    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )