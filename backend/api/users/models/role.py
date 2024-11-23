from pydantic import BaseModel


class RoleBase(BaseModel):
    roleType: str 