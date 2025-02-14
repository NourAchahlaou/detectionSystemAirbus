import os

from typing import Annotated, Generator, List, Tuple, Optional
import cv2
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from api.utils.database import get_db
from api.camera.models.camera import CameraBase
from api.camera.models.camera_settings import UpdateCameraSettings
from database.camera.camera import Camera
from hardware.camera.camera import FrameSource
import re

router = APIRouter()
db_dependency = Annotated[Session, Depends(get_db)]

frame_source = FrameSource()


@router.get("/get-index")
def get_camera_index(camera_id: int, db: db_dependency):
    camera_index = frame_source.get_camera_by_index(camera_id, db)
    if camera_index is None:
        raise HTTPException(status_code=404, detail=f"Camera with id {camera_id} not found")
    return {"camera_index": camera_index}



@router.get("/cameras/", response_model=List[Tuple[int, str]])
def read_cameras(db:db_dependency):

    cameras = frame_source.get_camera_model_and_ids(db)
    if not cameras:
        raise HTTPException(status_code=404, detail="No cameras found")
    return cameras



class CameraID(BaseModel):
    camera_id: int
# Endpoint to start a specific camera
@router.post("/start-camera")
def start_camera(camera: CameraID, db: db_dependency):
    frame_source.start(camera.camera_id, db)
    
    return {"message": "Camera started"}



@router.get("/video_feed")
def video_feed():
    return StreamingResponse(frame_source.generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")


@router.get("/camera_info/{camera_id}")
def get_camera_info(camera_id: int , db: db_dependency):
    return FrameSource.get_camera(camera_id, db)

@router.put("/{camera_id}")
async def change_camera_settings(camera_id: int, camera_settings_update: UpdateCameraSettings, db: db_dependency):
    return FrameSource.change_camera_settings(camera_id, camera_settings_update, db)

#didn't use this :
@router.get("/frame/{piece_label}")
async def get_frame(db: db_dependency, piece_label: str):
    if not frame_source.camera_is_running:
        raise HTTPException(status_code=400, detail="Camera is not running. Please start the camera first.")
    
    match = re.match(r'([A-Z]\d{3}\.\d{5})', piece_label)
    if not match:
        raise HTTPException(status_code=400, detail="Invalid piece_label format.")
    extracted_label = match.group(1)
    url = os.path.join("images","train",extracted_label,piece_label)
   
    # Define save_folder using the extracted_label
    save_folder = os.path.join('dataset','Pieces','Pieces','images','train',extracted_label,piece_label)
    os.makedirs(save_folder, exist_ok=True)
    
    try:
        frame = frame_source.next_frame(db, save_folder, url , piece_label)
    except SystemError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    if frame is None:
        raise HTTPException(status_code=500, detail="Failed to capture frame from the camera.")
    
    _, buffer = cv2.imencode('.jpg', frame)
    print("Frame captured and encoded")  # Add logging here
    return Response(content=buffer.tobytes(), media_type="image/jpeg")


# this is what will capture the images for the dataset
@router.get("/capture_images/{piece_label}")
async def capture_images( piece_label: str):
    if not frame_source.camera_is_running:
        raise HTTPException(status_code=400, detail="Camera is not running. Please start the camera first.")
    
    # Extract the part before the dot in the format "A123.4567"
    match = re.match(r'([A-Z]\d{3}\.\d{5})', piece_label)
    if not match:
        raise HTTPException(status_code=400, detail="Invalid piece_label format.")
    extracted_label = match.group(1)
    url = os.path.join('Pieces','Pieces','images',"valid",extracted_label, piece_label)
   
    # Define save_folder using the extracted_label
    save_folder = os.path.join ('dataset','Pieces','Pieces','images','valid',extracted_label,piece_label)
    os.makedirs(save_folder, exist_ok=True)
    
    try:
        frame = frame_source.capture_images(save_folder,url, piece_label)
    except SystemError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    if frame is None:
        raise HTTPException(status_code=500, detail="Failed to capture frame from the camera.")
    
    _, buffer = cv2.imencode('.jpg', frame)
    print("Frame captured and encoded")  # Add logging here
    return Response(content=buffer.tobytes(), media_type="image/jpeg")


@router.post("/cleanup-temp-photos")
async def cleanup_temp_photos_endpoint():
    frame_source.cleanup_temp_photos()
    return {"message": "Temporary photos cleaned up successfully"}


@router.post("/save-images")
def save_images(db: db_dependency, piece_label: str):
    try:
        frame_source.save_images_to_database(db,  piece_label)
    except SystemError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"message": "Images saved to database"}



@router.post("/stop")
def stop_camera():
    frame_source.stop()
    return {"message": "Camera stopped"}

@router.get("/check_camera")
async def check_camera():
    try:
        camera_status = frame_source._check_camera()
        return {"camera_opened": camera_status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))





@router.get("/get_allcameras/", response_model=List[dict])
def read_all_cameras(db: Session = Depends(get_db)):

    cameras = db.query(Camera.camera_index, Camera.model,Camera.id).all()
    return [{"camera_index": cam.camera_index, "model": cam.model,"camera_id": cam.id} for cam in cameras]

@router.get("/cameraByModelIndex/", response_model=int)
def read_camera_id(model: str, camera_index: int, db: Session = Depends(get_db)):

    camera_id = db.query(Camera.id).filter(
        Camera.model == model,
        Camera.camera_index == camera_index
    ).scalar()
    
    if camera_id is None:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    return camera_id







