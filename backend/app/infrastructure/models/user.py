from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.infrastructure.models.base import UUIDTimestampMixin


class User(UUIDTimestampMixin, Base):
    __tablename__ = "users"
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    accounts: Mapped[list["Account"]] = relationship(back_populates="user")  # noqa: F821
    trades: Mapped[list["Trade"]] = relationship(back_populates="user")  # noqa: F821

