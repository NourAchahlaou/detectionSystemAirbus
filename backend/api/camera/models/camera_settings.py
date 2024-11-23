from typing import Optional
from pydantic import BaseModel


class CameraSettingsBase (BaseModel) :
    
    exposure : float
    contrast : float
    brightness : float
    focus :float
    aperture :float
    gain : float
    frame_rate : int
    white_balance : float
    resolution: str

class CameraSettingsCreate(CameraSettingsBase):
    pass


class UpdateCameraSettings(BaseModel):
   
    exposure: Optional[float] = None
    contrast: Optional[float] = None
    brightness: Optional[float] = None
    focus: Optional[float] = None
    aperture: Optional[float] = None
    gain: Optional[int] = None
    frame_rate: Optional[int] = None
    white_balance: Optional[str] = None
    resolution: Optional[str] = None

    class Config:
        orm_mode = True

