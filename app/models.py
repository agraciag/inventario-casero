import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    pin: Mapped[str] = mapped_column(Text, nullable=False)  # hashed
    avatar_emoji: Mapped[str] = mapped_column(Text, default="📦")
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    boxes: Mapped[list["Box"]] = relationship(back_populates="creator")
    items: Mapped[list["Item"]] = relationship(back_populates="creator")


class Box(Base):
    __tablename__ = "boxes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    label: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str] = mapped_column(Text, default="")
    qr_code: Mapped[str] = mapped_column(Text, default=lambda: str(uuid.uuid4()))
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    creator: Mapped["User"] = relationship(back_populates="boxes")
    items: Mapped[list["Item"]] = relationship(back_populates="box")


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    box_id: Mapped[int | None] = mapped_column(ForeignKey("boxes.id"), nullable=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    photo_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    thumb_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[str] = mapped_column(Text, default="no_prioritario")
    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    estimated_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    box: Mapped["Box | None"] = relationship(back_populates="items")
    creator: Mapped["User"] = relationship(back_populates="items")


PRIORITY_CHOICES = [
    ("prioritario", "🟢 Prioritario", "green"),
    ("no_prioritario", "🔵 No prioritario", "blue"),
    ("quizas", "🟡 Quizás algún día", "yellow"),
    ("no_vale_la_pena", "🟠 No vale la pena", "orange"),
    ("tirar_regalar_vender", "🔴 Tirar/regalar/vender", "red"),
]
