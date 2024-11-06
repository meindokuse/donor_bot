from datetime import date
from typing import Optional
from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str
    telegram_id: str
    group: int
    rezus: str
    kell: str


class UserRead(BaseModel):
    id: int
    name: str
    telegram_id: str
    group: int
    rezus: str
    kell: str
