from sqlalchemy import Integer, Column, DateTime, ForeignKey, Boolean, String
from database.defectDetectionDB import Base
from sqlalchemy.orm import relationship


class Profile(Base):
    __tablename__='D.D.UserProfile'
    profile_id = Column(Integer, primary_key=True, index=True)
    is_active = Column(Boolean, default=True)
    password = Column(String, index= True)
    user_id = Column(String, ForeignKey('D.D.User.user_id'), unique=True)  # Adjust foreign key reference
    user = relationship("User", back_populates="profile")
    