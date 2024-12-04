from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship

from app.database.connection import session


class Thread(SQLModel, table=True):
    __tablename__ = "thread_tb"

    id: str = Field(primary_key=True)
    lesson_schedule_id: str = Field(foreign_key="lesson_schedule_tb.id")
    assistant_id: str = Field(foreign_key="assistant_tb.id")
    vector_store_id: str = Field(default=None)

    lesson_schedule: Optional["LessonSchedule"] = Relationship(back_populates="threads")
    assistant: Optional["Assistant"] = Relationship(back_populates="threads")
    messages: List["Message"] = Relationship(back_populates="thread")


def create_thread(thread: Thread):
    session.add(thread)


def get_thread(id: str):
    return session.query(Thread).filter(Thread.id == id).first()


def get_thread(assistant_id: int, lesson_schedule_id: int):
    return session.query(Thread).filter(Thread.lesson_schedule_id == lesson_schedule_id,
                                        Thread.assistant_id == assistant_id).first()
