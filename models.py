from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class GeneratedTextFile(Base):
    __tablename__ = "generated_textfiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now
    )
    
    completed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    url: Mapped[str] = mapped_column(Text, nullable=False)

    file_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    title: Mapped[str] = mapped_column(Text, nullable=True)