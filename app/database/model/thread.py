from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

from app.database.connection import session


class Thread(SQLModel, table=True):
    id: str = Field(primary_key=True, nullable=False)
    vector_store_id: Optional[str] = Field(unique=True, default=None)
    lesson_schedule_id: int = Field(unique=True, nullable=False)
    assistant_id: str = Field(foreign_key="assistant.id", nullable=False)

    # Relationship with assistant
    assistant: Optional["Assistant"] = Relationship(back_populates="threads")

    # Relationship with messages
    messages: List["Message"] = Relationship(back_populates="thread")


def create_thread(thread: Thread):
    session.add(thread)


def get_thread(id: str):
    return session.query(Thread).filter(Thread.id == id).first()


def get_thread(lesson_schedule_id: int):
    return session.query(Thread).filter(Thread.lesson_schedule_id == lesson_schedule_id).first()
