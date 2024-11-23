
import os
import re
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from api.utils.database import get_db
from sqlalchemy.orm import Session
from api.piece.models.annotation import AnnotationData

from database.piece.piece_image import PieceImage
from services.piece_service import delete_all_pieces, delete_piece_by_label, get_all_datasets, get_images_of_piece, get_img_non_annotated, save_annotation_in_memory, save_annotations_to_db


router = APIRouter()
db_dependency = Annotated[Session,Depends(get_db)]



@router.get("/image-id")
def get_image_id(url :str , db: db_dependency):
    piece_image = db.query(PieceImage).filter(PieceImage.url == url).first()
    if not piece_image:
        raise HTTPException(status_code=404, detail="Image not found")
    return {"image_id": piece_image.id}

@router.get("/get_images_of_piece/{piece_label}")
async def get_image_of_piece_byLabel(db:db_dependency,piece_label:str):
    return get_images_of_piece(piece_label,db)

@router.get("/get_Img_nonAnnotated")
def get_img_non_annotated_route(db: Session = Depends(get_db)):
    return get_img_non_annotated(db)


@router.post("/annotations/{piece_label}")
def create_annotation(piece_label: str, annotation_data: AnnotationData):

    # Extract image_id from the request body
    image_id = annotation_data.image_id

    if not image_id:
        raise HTTPException(status_code=400, detail="Missing image_id in annotation data.")
    
    # Save the annotation in virtual storage
    save_annotation_in_memory(piece_label, image_id, annotation_data.dict())

    return {"status": "Annotation saved in memory"}



@router.post("/saveAnnotation/{piece_label}")
def saveAnnotation (piece_label : str, db : db_dependency):
    print(f"Received piece_label: {piece_label}")
    
    # Ensure piece_label is provided
    if not piece_label:
        raise HTTPException(status_code=422, detail="piece_label is required")
    
    match = re.match(r'([A-Z]\d{3}\.\d{5})', piece_label)
    if not match:
        raise HTTPException(status_code=400, detail="Invalid piece_label format.")
    extracted_label = match.group(1)   
    # Define save_folder using the extracted_label
    save_folder = os.path.join("dataset","Pieces","Pieces", "labels", "valid", extracted_label, piece_label)
    os.makedirs(save_folder, exist_ok=True)
    try:
        result = save_annotations_to_db(db,piece_label,save_folder )
        result1 = get_images_of_piece(piece_label,db)
    except SystemError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    if result is None:
        raise HTTPException(status_code=500, detail="Failed to capture frame from the camera.")
    if result1 is None:
        raise HTTPException(status_code=500, detail="Failed to capture frame from the camera.")
    return piece_label , save_folder ,result,result1



@router.get("/datasets", tags=["Dataset"])
def get_datasets_route(db: Session = Depends(get_db)):
    """Route to fetch all datasets."""
    datasets = get_all_datasets(db)
    if not datasets:
        raise HTTPException(status_code=404, detail="No datasets found")
    return datasets



@router.delete("/delete_piece/{piece_label}")
def delete_piece(piece_label: str, db: db_dependency):
    return delete_piece_by_label(piece_label, db)

@router.delete("/delete_all_pieces")
def delete_all_pieces_route(db: db_dependency):
    return delete_all_pieces(db)