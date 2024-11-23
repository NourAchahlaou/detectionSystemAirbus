from sqlalchemy import Column, Integer, String

from database.defectDetectionDB import Base


class Role(Base):
    __tablename__='D.D.UserRole'
    role_id = Column(Integer, primary_key=True,index=True)
    roleType = Column(String, nullable=False)

