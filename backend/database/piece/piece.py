from sqlalchemy import Column, Integer, Null, String,Boolean
from sqlalchemy.orm import relationship
from database.defectDetectionDB import Base

class Piece(Base):
    __tablename__ = 'piece'

    id = Column(Integer, primary_key=True, index=True)
    class_data_id = Column(Integer,default = Null )
    piece_label = Column(String, nullable=False, unique=True)
    is_annotated = Column(Boolean,default=False)
    is_yolo_trained = Column(Boolean,default=False)
    nbre_img= Column(Integer,default = Null)
    # Define the one-to-many relationship with Piece_image
    piece_img = relationship("PieceImage", back_populates="piece", cascade="all, delete-orphan")
    