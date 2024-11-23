from typing import Optional
from pydantic import BaseModel, EmailStr

from api.users.models.role import RoleBase


class UserBase(BaseModel):
    user_id:str  
    email: EmailStr
    firstName: str  
    secondName: str
    password : str
    role: Optional[RoleBase]
      

# Assuming UserUpdate is used for updating specific fields
class UserUpdate(BaseModel):
    user_id: Optional[str] = None
    email: Optional[EmailStr] = None
    firstName: Optional[str] = None
    secondName: Optional[str] = None
    password: Optional[str] = None  # Optional since it's only needed when changing password
    role: Optional['RoleBase'] = None

    class Config:
        orm_mode = True
 