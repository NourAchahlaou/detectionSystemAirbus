from pydantic import BaseModel
from typing import List
from piece_image import PieceImage


class PieceBase(BaseModel):
    piece_label: str
    piece_path: str

class PieceCreate(PieceBase):
    pass

class Piece(PieceBase):
    id: int
    piece_img: List[PieceImage] = []

    class Config:
        orm_mode = True
