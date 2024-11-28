import os

from sqlalchemy import *
from sqlalchemy.orm import sessionmaker


username = os.getenv("DB_USERNAME")
password = os.getenv("DB_PASSWORD")
port = os.getenv("DB_PORT")
host = os.getenv("DB_HOST")
name = os.getenv("DB_NAME")

DB_URL = f'mysql+pymysql://{username}:{password}@{host}:{port}/{name}'
engine = create_engine(DB_URL, echo=True)
Session = sessionmaker()
Session.configure(bind=engine)

session = Session()
