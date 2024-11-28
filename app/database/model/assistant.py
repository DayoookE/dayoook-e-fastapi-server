from typing import List
from sqlmodel import SQLModel, Field, Relationship
from app.database.connection import session


class Assistant(SQLModel, table=True):
    id: str = Field(primary_key=True, nullable=False)
    user_id: int = Field(nullable=False)

    # Relationship with thread
    threads: List["Thread"] = Relationship(back_populates="assistant")


def get_assistant(user_id: int):
    return session.query(Assistant).filter(Assistant.user_id == user_id).first()


def create_assistant(assistant: Assistant):
    session.add(assistant)
