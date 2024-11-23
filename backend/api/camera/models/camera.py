
from typing import Optional
from pydantic import BaseModel

from database.camera.camera_settings import CameraSettings


class CameraBase (BaseModel):
    camera_index : int 
    model:str
    status : bool
    settings_id: int
   


class CameraCreate(CameraBase):
    pass

class CameraUpdate(BaseModel):
    camera_index : Optional[int] = None
    model: Optional[str] = None
    status: Optional[bool] = None
    settings_id: Optional[int] = None

