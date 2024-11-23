from pydantic import BaseModel
from typing import  Optional
from datetime import datetime

class PieceImageBase(BaseModel):
    piece_label: str
    piece_path: str
    timestamp: Optional[datetime] = None


class ImageURLRequest(BaseModel):
    url: str
    
class PieceImageCreate(PieceImageBase):
    pass

class PieceImage(PieceImageBase):
    id: int
    piece_id: int

    class Config:
        orm_mode = True
