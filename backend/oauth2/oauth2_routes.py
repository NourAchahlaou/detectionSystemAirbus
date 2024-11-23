from datetime import timedelta , datetime
import traceback
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Annotated, List
from api.utils.database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from oauth2.customOauth import CustomOAuth2PasswordRequestFormStrict
from api.users.models.user import UserBase as User
from oauth2.oauth2 import ACCESS_TOKEN_EXPIRE_MINUTES, authenticate_user, create_access_token, get_current_active_user
from oauth2.oauth2_model import Token
from database.users.session import Session as SessionModel
from database.users.profile import Profile

router = APIRouter()
db_dependency = Annotated[Session, Depends(get_db)]

@router.post("/auth")
async def login (user_id:str,user_pwd:str,db : db_dependency):
    return authenticate_user(db,user_id,user_pwd)

@router.post("/logout")
async def logout(current_user: Annotated[User, Depends(get_current_active_user)], db: Session = Depends(get_db)):
    try:
        # Retrieve the current user's session
        session = db.query(SessionModel).filter(SessionModel.user_id == current_user.user_id, SessionModel.logout_time == None).first()
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Active session not found")
        
        # Update the logout time
        session.logout_time = datetime.utcnow()
        db.commit()
        
        # Update the user's profile to inactive
        profile = db.query(Profile).filter(Profile.user_id == current_user.user_id).first()
        if profile:
            profile.is_active = False
            db.commit()
        
        return {"msg": "User successfully logged out"}
    
    except Exception as e:
        db.rollback()  # Roll back in case of an error
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error logging out")



@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
):
    try:
        user_id = form_data.username
        user = authenticate_user(db, user_id, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect user ID or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create a new session record
        session = SessionModel(user_id=user.user_id, login_time=datetime.utcnow())
        db.add(session)
        db.commit()
        
        # Retrieve and update the user's profile
        profile = db.query(Profile).filter(Profile.user_id == user.user_id).first()
        if profile:
            profile.is_active = True
            db.commit()  # Commit changes to the database
        
        # Generate access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"sub": user.user_id}, expires_delta=access_token_expires)
        return {"access_token": access_token, "token_type": "bearer"}
    
    except HTTPException as e:
        raise e
    except Exception as e:
        traceback.print_exc()  # Print the stack trace to the console for debugging
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again later."
        )

@router.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user

@router.get("/users/me/greetings/")
async def greetings(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return [{"hello":current_user.firstName, "owner": current_user.user_id}]