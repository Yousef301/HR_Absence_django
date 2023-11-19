from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine

engine = create_engine("mysql://root:yousefQ1@localhost:3306/hr")


def get_session():
    return scoped_session(sessionmaker(bind=engine))
