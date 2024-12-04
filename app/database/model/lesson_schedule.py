from typing import List, Optional

from sqlmodel import SQLModel, Field, Relationship

from app.database.connection import session


class LessonSchedule(SQLModel, table=True):
    __tablename__ = "lesson_schedule_tb"

    id: str = Field(primary_key=True)
    audio_url: str = Field(default=None)
    dialogue_url: str = Field(default=None)
    review_url: str = Field(default=None)
    user_id: int = Field(foreign_key="user_tb.id")

    user: Optional["User"] = Relationship(back_populates="lesson_schedules")
    threads: List["Thread"] = Relationship(back_populates="lesson_schedule")


def get_lesson_schedule(id: str, user_id: int):
    session.query(LessonSchedule).filter(LessonSchedule.id == id,
                                         LessonSchedule.user_id == user_id)


def merge_lesson_schedule(lesson_schedule: LessonSchedule):
    session.merge(lesson_schedule)
