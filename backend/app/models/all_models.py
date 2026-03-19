from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from typing import List, Optional
import enum

class Base(DeclarativeBase):
    pass

class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    created_at: Mapped[Optional[func.now]] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    tasks: Mapped[List["Task"]] = relationship(back_populates="owner")

class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String, default=TaskStatus.PENDING)
    result: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    owner_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[Optional[func.now]] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[func.now]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    owner: Mapped[Optional["User"]] = relationship(back_populates="tasks")
    executions: Mapped[List["Execution"]] = relationship(back_populates="task", cascade="all, delete")

class Execution(Base):
    __tablename__ = "executions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"))
    status: Mapped[str] = mapped_column(String)
    start_time: Mapped[Optional[func.now]] = mapped_column(DateTime(timezone=True), server_default=func.now())
    end_time: Mapped[Optional[func.now]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    task: Mapped["Task"] = relationship(back_populates="executions")
