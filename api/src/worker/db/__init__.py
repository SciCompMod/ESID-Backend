from core.config import DATABASE_URL
from sqlmodel import Session, create_engine

engine = create_engine(str(DATABASE_URL), echo=True, future=True)


def get_session():
    with Session(engine) as session:
        yield session