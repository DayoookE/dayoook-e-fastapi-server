from datetime import datetime
from typing import Optional

from sqlalchemy import String
from sqlmodel import SQLModel, Field, Relationship

from app.database.connection import session


class Message(SQLModel, table=True):
    __tablename__ = "message_tb"

    id: str = Field(primary_key=True)
    thread_id: str = Field(foreign_key="thread_tb.id")
    question: str = Field(default=None, sa_type=String(2000))
    answer: str = Field(default=None, sa_type=String(2000))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    thread: Optional["Thread"] = Relationship(back_populates="messages")


def create_message(message: Message):
    session.add(message)


def get_message(id: str):
    return session.query(Message).filter(Message.id == id).first()


def get_messages_by_thread_id(thread_id: str):
    return session.query(Message).filter(Message.thread_id == thread_id).all()
