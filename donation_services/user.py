from datetime import date
from typing import Optional
from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str
    telegram_id: str
    email: Optional[str]
    password: str

class UserRead(BaseModel):
    id:int
    name: str
    telegram_id: str
    email: Optional[str]
    role_id: int
    registered_on: date



class RegRequestCreate(BaseModel):
    name: str
    telegram_id: str
    email: Optional[str]
    password: str


class RegRequestRead(BaseModel):
    id:int
    name: str
    telegram_id: str
    email: Optional[str]