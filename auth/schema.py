from typing import Optional
from sqlmodel import (
    Field,
    SQLModel,
    create_engine,
)


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    email: str
    contact: int


class Container(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int | None = Field(default=None, foreign_key='user.id')
    image_name: str
    price: int


class Billing(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int | None = Field(default=None, foreign_key='user.id')
    total: int


engine = "postgresql://postgres:127.0.0.1:"
