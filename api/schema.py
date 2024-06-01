import os
from typing import Optional
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from sqlmodel import (
    Field,
    SQLModel,
    Session,
    create_engine,
)

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    uuid: str = Field(sa_column_kwargs={"unique": True})
    username: str
    email: str
    password: str
    balance: int = 0
    def to_safe_dict(self):
        return {key: value for key, value in self.__dict__.items() if key != 'password'}

class Payment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int | None = Field(default=None, foreign_key='user.id')
    order_id: str

class Container(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int | None = Field(default=None, foreign_key='user.id')
    image_name: str
    price: int


class Billing(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int | None = Field(default=None, foreign_key='user.id')
    total: int


from urllib.parse import quote_plus
load_dotenv()
DB_PASS = quote_plus(os.getenv("DB_PASS"))

DB_URL = f"postgresql://postgres:{DB_PASS}@cloudDB:5432/postgres"
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

SQLModel.metadata.create_all(engine)

def get_db():
    with Session(engine) as session:
        yield session