from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship
from app.database.connection import session


class Assistant(SQLModel, table=True):
    __tablename__ = "assistant_tb"

    id: str = Field(primary_key=True)
    user_id: str = Field(foreign_key="user_tb.id")
    role: str = Field(default=None)

    user: Optional["User"] = Relationship(back_populates="assistants")
    threads: List["Thread"] = Relationship(back_populates="assistant")


def get_chat_assistant(user_id: int):
    return session.query(Assistant).filter(Assistant.user_id == user_id).first()


def create_assistant(assistant: Assistant):
    session.add(assistant)
