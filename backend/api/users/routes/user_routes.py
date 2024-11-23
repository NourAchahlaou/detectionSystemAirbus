from typing import Annotated,List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.users.models.user import UserBase, UserUpdate
from api.users.models.role import RoleBase
from api.utils.database import get_db
from oauth2.oauth2 import get_current_active_user
from services.user_service import (
    create_user, update_user_role, get_user_byId, 
    get_sessions_by_user_id, update_user, delete_user, delete_profile,
    get_all_users

)

router = APIRouter()
db_dependency = Annotated[Session, Depends(get_db)]

@router.get("/profile")
async def get_profile(current_user: Annotated[UserBase, Depends(get_current_active_user)]):
    return current_user  # Assuming current_user has a profile attribute

@router.get("/getUserByID/{user_id}")
async def get_user_by_Id(user_id: str, db: db_dependency):
    return get_user_byId(db, user_id)

@router.get("/users")
def read_all_users(db: db_dependency):
    return get_all_users(db)

@router.post("/createUser")
async def create_user_route(user: UserBase, db: db_dependency):
    return create_user(user, db)

@router.put("/updateUserRole/{user_id}")
async def update_user_role_route(user_id: str, role: RoleBase, db: db_dependency):
    return update_user_role(user_id, role, db)

@router.put("/updateUser/{user_id}")
async def update_user_route(user_id: str, user_update: UserUpdate, db: db_dependency):
    return update_user(user_id, user_update, db)

@router.delete("/deleteUser/{user_id}")
async def delete_user_route(user_id: str, db: db_dependency):
    return delete_user(user_id, db)

@router.delete("/deleteProfile/{user_id}")
async def delete_profile_route(user_id: str, db: db_dependency):
    return delete_profile(user_id, db)

@router.get("/users/{user_id}/sessions")
async def fetch_user_sessions(user_id: str, db: Session = Depends(get_db)):
    try:
        sessions = get_sessions_by_user_id(db, user_id)
        if not sessions:
            raise HTTPException(status_code=404, detail="No sessions found for this user")
        return sessions
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while fetching sessions")
