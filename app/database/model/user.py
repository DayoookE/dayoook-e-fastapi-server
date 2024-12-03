from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List


class User(SQLModel, table=True):
    __tablename__ = "user_tb"

    id: str = Field(primary_key=True)
    chat_assistant_id: str = Field(nullable=False)
    review_assistant_id: str = Field(nullable=False)

    assistants: List["Assistant"] = Relationship(back_populates="user")