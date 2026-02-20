from sqlalchemy import Integer, DateTime, UUID, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
import uuid
from datetime import datetime
from app.core.database import Base


class UserPlanHistory(Base):
    __tablename__ = "user_plan_histories"

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

    plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("plans.id"),
        nullable=False
    )

    storage_used: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    ended_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )