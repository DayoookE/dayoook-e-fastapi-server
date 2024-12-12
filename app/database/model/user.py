from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

from app.database.connection import session


class User(SQLModel, table=True):
    __tablename__ = "user_tb"

    id: int = Field(primary_key=True)
    chat_assistant_id: str = Field(nullable=True, default=None)
    review_assistant_id: str = Field(nullable=True, default=None)

    assistants: List["Assistant"] = Relationship(back_populates="user")
    lesson_schedules: List["LessonSchedule"] = Relationship(back_populates="user")


def get_user(user_id: int):
    return session.query(User).filter(User.id == user_id).first()


def create_user(user: User):
    session.add(user)


def merge_user(user: User):
    session.merge(user)
