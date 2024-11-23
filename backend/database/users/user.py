from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from database.defectDetectionDB import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = 'D.D.User'
    user_id = Column(String, primary_key=True, index=True)
    # index for better performance when querying by id
    firstName = Column(String, index=True)
    secondName = Column(String, index=True)   
    email = Column(String, unique=True, index=True)
    role_id = Column(Integer, ForeignKey('D.D.UserRole.role_id'))
    profile = relationship("Profile", uselist=False, back_populates="user")
    inspection_images = relationship("InspectionImage", back_populates="user")
    sessions = relationship("Session", back_populates="user")