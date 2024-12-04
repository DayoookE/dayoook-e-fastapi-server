from sqlmodel import SQLModel

from app.database.connection import session, engine
from app.database.model import user
from app.database.model import lesson_schedule
from app.database.model import assistant
from app.database.model import thread
from app.database.model import message


def commit():
    session.commit()


def rollback():
    session.rollback()


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)