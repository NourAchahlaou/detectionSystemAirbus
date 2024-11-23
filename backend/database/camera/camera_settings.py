from sqlalchemy import Integer, Column, String, Float
from database.defectDetectionDB import Base
from sqlalchemy.orm import relationship

class CameraSettings (Base):
    __tablename__ = 'cameraSettings'

    id = Column(Integer, primary_key=True, index=True)
    # Exposure settings in the camera
    exposure = Column(Float)
    # Contrast adjustment for the image
    contrast = Column(Float)
    # Brightness adjustment for the image
    brightness = Column(Float)
    #Adjusts the sharpness of the image by controlling where the lens is focused.
    focus = Column(Float)
    #Regulates the amount of light that passes through the lens.
    aperture= Column (Float)
    #Adjusts the camera's sensitivity to light.
    gain = Column(Integer)
    # #Specifies how many frames (images) per second the camera captures.FPS
    # frame_rate =Column(Integer)
    #Adjusts the color balance of the image to accurately represent colors under different lighting conditions.
    white_balance = Column(String)
    # #Specifies the size and detail of the image or video in terms of pixels.
    # resolution = Column(String)

    camera = relationship("Camera", back_populates="sittings", uselist=True)
