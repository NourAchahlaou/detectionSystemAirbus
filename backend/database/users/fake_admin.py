from sqlalchemy.orm import Session
from passlib.context import CryptContext
from database.users.user import User
from database.users.profile import Profile

# Password hashing utility
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_admin_user(db: Session):
    # Check if any users exist in the User table
    if not db.query(User).first():
        print("No users found. Creating a default admin user...")
        
        # Create a hashed password
        hashed_password = pwd_context.hash("admin123")  # Replace with a secure password
        
        # Create the admin user
        admin_user = User(
            user_id="admin",
            firstName="Admin",
            secondName="User",
            email="admin@example.com",
            role_id=1  # Assume role_id 1 is for admins
        )
        
        # Create the admin profile
        admin_profile = Profile(
            is_active=True,
            password=hashed_password,
            user_id="admin"
        )
        
        # Add admin user and profile to the database
        db.add(admin_user)
        db.add(admin_profile)
        db.commit()
        print("Admin user created successfully.")
    else:
        print("Users already exist. Skipping admin creation.")
