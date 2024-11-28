from datetime import datetime
from typing import Optional

from sqlalchemy import String
from sqlmodel import SQLModel, Field, Relationship

from app.database.connection import session


class Message(SQLModel, table=True):
    id: str = Field(primary_key=True, nullable=False)
    question: Optional[str] = Field(default=None, sa_type=String(1500))
    answer: Optional[str] = Field(default=None, sa_type=String(1500))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    thread_id: str = Field(foreign_key="thread.id", nullable=False)

    # Relationship with thread
    thread: Optional["Thread"] = Relationship(back_populates="messages")


def create_message(message: Message):
    session.add(message)


def get_message(id: str):
    return session.query(Message).filter(Message.id == id).first()


def get_messages_by_thread_id(thread_id: str):
    return session.query(Message).filter(Message.thread_id == thread_id).all()
