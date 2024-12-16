from typing import List, Optional

from sqlalchemy import String
from sqlmodel import SQLModel, Field, Relationship

from app.database.connection import session


class LessonSchedule(SQLModel, table=True):
    __tablename__ = "lesson_schedule_tb"

    id: str = Field(primary_key=True)
    audio_url: str = Field(nullable=True, default=None)
    dialogue_url: str = Field(nullable=True, default=None)
    review: str = Field(nullable=True, default=None, sa_type=String(10000))
    review_completed: bool = Field(nullable=False, default=False)
    tutor_id: int = Field(nullable=False, default=None)

    threads: List["Thread"] = Relationship(back_populates="lesson_schedule")


def get_lesson_schedule_by_userid(id: int, user_id: int):
    return session.query(LessonSchedule).filter(LessonSchedule.id == id,
                                                LessonSchedule.tutor_id == user_id).first()


def get_lesson_schedule(id: int):
    return session.query(LessonSchedule).filter(LessonSchedule.id == id).first()


def get_lesson_schedules(user_id: int):
    return session.query(LessonSchedule).filter(LessonSchedule.tutor_id == user_id).all()


def merge_lesson_schedule(lesson_schedule: LessonSchedule):
    return session.merge(lesson_schedule)
