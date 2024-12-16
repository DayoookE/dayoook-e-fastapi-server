from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship
from app.database.connection import session


class Assistant(SQLModel, table=True):
    __tablename__ = "assistant_tb"

    id: str = Field(primary_key=True)
    user_id: int = Field(foreign_key="user_tb.id")
    role: str = Field(default=None)

    user: Optional["User"] = Relationship(back_populates="assistants")
    threads: List["Thread"] = Relationship(back_populates="assistant")


def get_assistant_by_role(role: str):
    return session.query(Assistant).filter(Assistant.role == role).first()


def create_assistant(assistant: Assistant):
    session.add(assistant)
