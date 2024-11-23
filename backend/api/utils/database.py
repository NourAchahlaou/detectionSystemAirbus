from database.users.role import Role
from database.users.roleEnum import RoleEnum
from database.defectDetectionDB import SessionLocal
from sqlalchemy.orm import Session





# Function to initialize roles on application startup
def initialize_roles(db: Session):
    for role_name in RoleEnum:
        db_role = db.query(Role).filter(Role.roleType == role_name.value).first()
        if not db_role:
            db_role = Role(roleType=role_name.value)
            db.add(db_role)
    db.commit()


def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()  

