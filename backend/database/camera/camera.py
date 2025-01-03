from sqlalchemy import Boolean, String, Column,Integer,ForeignKey
from database.defectDetectionDB import Base
from sqlalchemy.orm import relationship

from sqlalchemy import Boolean, String, Column, Integer, ForeignKey
from database.defectDetectionDB import Base
from sqlalchemy.orm import relationship

class Camera(Base):
    __tablename__ = 'camera'

    id = Column(Integer, primary_key=True, index=True)
    camera_type = Column(String, nullable=False)  # "regular" or "industrial"
    camera_index = Column(Integer, nullable=True)  # For regular cameras
    serial_number = Column(String, unique=True, nullable=True)  # For industrial cameras
    model = Column(String, index=True)  
    status = Column(Boolean, default=False)
    settings_id = Column(Integer, ForeignKey('cameraSettings.id'))
    sittings = relationship("CameraSettings", back_populates="camera")