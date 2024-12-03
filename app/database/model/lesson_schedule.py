from typing import List

from sqlmodel import SQLModel, Field, Relationship


class LessonSchedule(SQLModel, table=True):
    __tablename__ = "lesson_schedule_tb"

    id: str = Field(primary_key=True)
    audio_url: str = Field(default=None)
    dialogue_url: str = Field(default=None)
    review_url: str = Field(default=None)

    threads: List["Thread"] = Relationship(back_populates="lesson_schedule")

