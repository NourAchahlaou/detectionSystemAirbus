import datetime
from typing import Optional
from pydantic import BaseModel


class ProfileBase(BaseModel):
    user_id: str  
    is_active: bool = False