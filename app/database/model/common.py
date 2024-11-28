from sqlmodel import SQLModel

from app.database.connection import session, engine
from app.database.model import *


def commit():
    session.commit()


def rollback():
    session.rollback()


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)