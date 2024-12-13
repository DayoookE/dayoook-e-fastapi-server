from typing import List, Optional

from sqlmodel import SQLModel, Field, Relationship

from app.database.connection import session


class LessonSchedule(SQLModel, table=True):
    __tablename__ = "lesson_schedule_tb"

    id: str = Field(primary_key=True)
    audio_url: str = Field(nullable=True, default=None)
    dialogue_url: str = Field(nullable=True, default=None)
    review: str = Field(nullable=True, default=None)
    review_completed: bool = Field(nullable=False, default=False)
    user_id: int = Field(foreign_key="user_tb.id")

    user: Optional["User"] = Relationship(back_populates="lesson_schedules")
    threads: List["Thread"] = Relationship(back_populates="lesson_schedule")


def get_lesson_schedule(id: int, user_id: int):
    return session.query(LessonSchedule).filter(LessonSchedule.id == id,
                                                LessonSchedule.user_id == user_id).first()

def get_lesson_schedules(user_id : int):
    return session.query(LessonSchedule).filter(LessonSchedule.user_id == user_id).all()

def merge_lesson_schedule(lesson_schedule: LessonSchedule):
    return session.merge(lesson_schedule)
