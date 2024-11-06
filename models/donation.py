from typing import Optional
from pydantic import BaseModel
from datetime import date

class Donation(BaseModel):
    owner: str
    type: str
    data: date
    org: str
    free: bool
    
