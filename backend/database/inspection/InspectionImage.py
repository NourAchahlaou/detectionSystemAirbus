from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database.defectDetectionDB import Base

class InspectionImage(Base):
    __tablename__ = "inspection_image"

    id = Column(Integer, primary_key=True, index=True)
    image_path = Column(String, nullable=False)
    image_name = Column(String, nullable=False)
    order_of_fabrication = Column(String, nullable=False)
    target_label = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    #add type of image ( inspection or identification)
    type = Column(String, nullable=False) 
    user_id = Column(String, ForeignKey('D.D.User.user_id'), nullable=False)
    user = relationship("User", back_populates="inspection_images")
    