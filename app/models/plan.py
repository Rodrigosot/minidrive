from sqlalchemy import String, Integer, UUID
from sqlalchemy.orm import Mapped, mapped_column
import uuid
from app.core.database import Base


class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )

    name: Mapped[str] = mapped_column(
        String,
        unique=True,
        index=True,
        nullable=False
    )

    storage_limit: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    price_per_month: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )