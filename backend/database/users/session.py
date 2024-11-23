from sqlalchemy import Column, DateTime, Integer,String , ForeignKey
from database.defectDetectionDB import Base
from sqlalchemy.orm import relationship

class Session(Base):
    __tablename__ = 'D.D.UserSession'
    
    session_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey('D.D.User.user_id'))
    login_time = Column(DateTime)
    logout_time = Column(DateTime)
    
    user = relationship("User", back_populates="sessions")
    
