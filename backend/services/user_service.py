from fastapi import Depends, HTTPException
from typing import Annotated, List

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from database.users.user import User
from database.users.role import Role
from database.users.profile import Profile
from api.users.models.user import UserBase, UserUpdate
from api.users.models.role import RoleBase
from api.users.models.profile import ProfileBase
import logging
from passlib.context import CryptContext

from database.users.session import Session as SessionModel

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def get_user_byId(db: Session, user_id: str) -> User | None:
    db_user = db.query(User).filter(User.user_id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

def get_all_users(db: Session) -> List[User] | None:
    try:
        users = db.query(User).all()
        if not users:
            raise HTTPException(status_code=404, detail="No users found")
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while fetching users: {str(e)}")
def create_user(user: UserBase, db: Session):
    try:
        # Check for existing user before creating a new one
        existing_user = db.query(User).filter((User.user_id == user.user_id) | (User.email == user.email)).first()
        if existing_user:
            logger.warning(f"User already exists: {existing_user.user_id}, {existing_user.email}")
            raise HTTPException(status_code=400, detail="User ID or Email address already exists")

        # Hash the user's password and store it in Profile
        hashed_password = get_password_hash(user.password)

        # Create the user instance without a password
        db_user = User(
            user_id=user.user_id,
            firstName=user.firstName,
            secondName=user.secondName,
            email=user.email
        )

        # Set the user's role if provided
        if user.role:
            role_name = user.role.roleType
            db_role = db.query(Role).filter(Role.roleType == role_name).first()
            if not db_role:
                logger.warning(f"Role '{role_name}' not found for user {user.user_id}")
                raise HTTPException(status_code=404, detail=f"Role '{role_name}' not found")
            db_user.role_id = db_role.role_id

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        # Create a profile for the new user and set the password in the Profile
        db_profile = Profile(
            user_id=db_user.user_id,
            is_active=False,
            password=hashed_password
        )
        db.add(db_profile)
        db.commit()
        db.refresh(db_profile)

        # Return the created user and profile
        logger.info(f"User created successfully: {db_user.user_id}, profile: {db_profile.profile_id}")
        return db_user

    except IntegrityError as e:
        db.rollback()
        logger.error(f"IntegrityError: {e}")
        raise HTTPException(status_code=400, detail="User ID or Email address already exists")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"SQLAlchemyError occurred: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Unexpected server error occurred")


def update_user_role(user_id: str, role: RoleBase, db: Session):
    db_user = db.query(User).filter(User.user_id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    role_name = role.roleType
    db_role = db.query(Role).filter(Role.roleType == role_name).first()
    if not db_role:
        raise HTTPException(status_code=404, detail=f"Role '{role_name}' not found")
    
    db_user.role_id = db_role.role_id
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(user_id: str, user_update: UserUpdate, db: Session):
    db_user = db.query(User).filter(User.user_id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update user fields
    if user_update.firstName:
        db_user.firstName = user_update.firstName
    if user_update.secondName:
        db_user.secondName = user_update.secondName
    if user_update.email:
        db_user.email = user_update.email

    # Update fields in Profile if needed
    if user_update.password:
        db_user.profile.password = get_password_hash(user_update.password)

    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(user_id: str, db: Session):
    db_user = db.query(User).filter(User.user_id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(db_user)
    db.commit()
    return {"detail": f"User with ID {user_id} has been deleted"}

def delete_profile(user_id: str, db: Session):
    db_profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    if not db_profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    db.delete(db_profile)
    db.commit()
    return {"detail": f"Profile for user with ID {user_id} has been deleted"}

def get_sessions_by_user_id(db: Session, user_id: str):
    return db.query(SessionModel).filter(SessionModel.user_id == user_id).all()
