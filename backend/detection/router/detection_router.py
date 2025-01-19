import cv2
import asyncio
import io
import logging
import threading
import numpy as np
from typing import Annotated, AsyncGenerator
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from detection.service.model_training_service import train_model, stop_training
from detection.service.detection_service import DetectionSystem
from hardware.camera.camera import FrameSource
from api.utils.database import get_db
import time
from database.inspection.InspectionImage import InspectionImage
import os
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(),
                              logging.FileHandler("training_logs.log", mode='a')])

logger = logging.getLogger(__name__)

router = APIRouter()
db_dependency = Annotated[Session, Depends(get_db)]
stop_event = threading.Event()  # Event to signal when to stop

# Initialize FrameSource and DetectionSystem
frame_source = FrameSource()
detection_system = None  # We'll initialize this globally to avoid loading it multiple times.

async def load_model_once():
    """Load the model once when the application starts to avoid reloading it for each frame."""
    global detection_system
    if detection_system is None:
        detection_system = DetectionSystem()
        detection_system.get_my_model()  # Load the model once


async def process_frame(frame: np.ndarray, target_label: str):
    """Asynchronously process a single frame to perform detection and contouring."""
    try:
        detection_results = detection_system.detect_and_contour(frame, target_label)
        if isinstance(detection_results, tuple):
            processed_frame = detection_results[0]
            detected_target = detection_results[1] if len(detection_results) > 1 else False
            non_target_count = detection_results[2] if len(detection_results) > 2 else 0
        else:
            processed_frame = detection_results
            detected_target = False
            non_target_count = 0
        
        return processed_frame, detected_target, non_target_count
    except cv2.error as e:
        logging.error(f"OpenCV error: {e}")
        return frame, False, 0
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return frame, False, 0


async def generate_frames(camera_id: int, target_label: str, db: Session) -> AsyncGenerator[bytes, None]:
    """Generate video frames asynchronously and perform detection on them."""
    frame_source.start(camera_id, db)
    
    detection_time = time.time()
    timeout_duration = 60  # seconds
    object_detected = False  # To track whether an object has been detected

    frame_counter = 0
    process_interval = 5  # Process every 5 frames
    
    try:
        while not stop_event.is_set():
            logging.debug("Stop event not set, continuing loop.")
            if frame_source.camera_is_running:
                logging.debug("Camera is running.")
                frame = frame_source.frame()
                if frame is None:
                    logging.debug("No frame captured.")
                    await asyncio.sleep(0)  # Yield control to the event loop
                    continue

                # Process only every N frames to reduce load
                if frame_counter % process_interval == 0:
                    if not isinstance(frame, np.ndarray):
                        logging.error("Captured frame is not a NumPy array.")
                        continue

                    if frame.ndim != 3 or frame.dtype != np.uint8:
                        logging.error(f"Frame dimensions or data type are incorrect. Dimensions: {frame.ndim}, Data type: {frame.dtype}")
                        continue

                    processed_frame, detected_target, non_target_count = await process_frame(frame, target_label)

                    if non_target_count > 0:
                        logging.error(f"Detected {non_target_count} pieces that do not belong.")
                    
                    if detected_target:
                        object_detected = True
                        detection_time = time.time()
                    
                    if processed_frame.shape[2] == 3:
                        _, buffer = cv2.imencode('.jpg', processed_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
                        if not _:
                            logging.error("Failed to encode frame.")
                            continue

                        image_stream = io.BytesIO(buffer)
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + image_stream.getvalue() + b'\r\n')
                    else:
                        logging.error("Processed frame is not in BGR format.")
                    
                frame_counter += 1

                # Timeout logic if no object is detected
                if time.time() - detection_time > timeout_duration and not object_detected:
                    logging.debug("Timeout reached without object detection, stopping.")
                    break
            else:
                logging.debug("Camera is not running.")
                break

            await asyncio.sleep(0)  # Yield control to the event loop

    finally:
        logging.debug("Stopping frame source.")
        stop_video()
        stop_event.clear()  # Clear the event for the next use
        frame_source.stop()
        logging.debug("Stop event cleared.")


@router.get("/video_feed")
async def video_feed(camera_id: int, target_label: str, db: Session = Depends(get_db)):
    # Ensure the model is loaded once before generating frames
    await load_model_once()
    return StreamingResponse(generate_frames(camera_id, target_label, db), media_type='multipart/x-mixed-replace; boundary=frame')


def stop_video():
    """Stop video streaming."""
    stop_event.set()
    logger.info("Stop video signal sent.")


@router.post("/train/{piece_label}")
def train_piece_model(piece_label: str, db: Session = Depends(get_db)):
    try:
        # Call the train_model function
        train_model(piece_label, db)
        return {"message": "Training process started. Check logs for updates."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")


@router.post("/stop_training")
async def stop_training_yolo():
    try:
        await stop_training()
        return {"message": "Stop training signal sent."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")


@router.post("/stop_camera_feed")
async def stop_camera_feed():
    try:
        stop_video()  # Ensure this is the function to stop the feed
        return {"message": "Camera feed stopped successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")



# Directory to save captured images
SAVE_DIR = "captured_images"

if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)  # Create the directory if it doesn't exist

async def capture_frame(camera_id: int,of: str, target_label: str, user_id:str, db: Session = Depends(get_db)):
    await load_model_once()  
    
  
    frame_source.start(camera_id, db)
    
    try:
        frame = frame_source.frame()
        if frame is None:
            raise HTTPException(status_code=500, detail="No frame captured from the camera.")
        
        # Detect object in the frame
        processed_frame, detected_target, _ = await process_frame(frame, target_label)
        
        if detected_target:
            # Save the frame with the detected object
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_name = f"captured_{target_label}_{timestamp}_{user_id}.jpg"
            image_path = os.path.join(SAVE_DIR, image_name)
            
            if processed_frame.shape[2] == 3:
                # Encode and save the image as a JPEG file
                success, buffer = cv2.imencode('.jpg', processed_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
                if not success:
                    raise HTTPException(status_code=500, detail="Failed to encode frame.")
                
                with open(image_path, 'wb') as f:
                    f.write(buffer.tobytes())
                
                logging.info(f"Captured image saved at {image_path}")
                
                # Save the image details to the database
                try:
                    logging.info("Preparing to save image details to the database.")
                    
                    inspection_image = InspectionImage(
                        image_path=image_path,
                        image_name=image_name,
                        order_of_fabrication=of,  # Replace with actual data
                        target_label=target_label,
                        created_at=datetime.now(),
                        type= "inspection",
                        user_id=user_id,
                    )

                    # Log the details being saved
                    logging.info(f"Image details: {inspection_image}")

                    db.add(inspection_image)
                    db.commit()  # Commit the transaction
                    
                    # Log success message
                    logging.info(f"Image details saved successfully with ID: {inspection_image.id}")

                except Exception as e:
                    logging.error(f"Error saving image details to the database: {str(e)}")
                    raise HTTPException(status_code=500, detail=f"An error occurred while saving image details: {str(e)}")
                                
                return {"message": "Image captured and saved.", "file_path": image_path, "db_entry": inspection_image.id}
            else:
                raise HTTPException(status_code=500, detail="Processed frame is not in the correct format (BGR).")
        else:
            return {"message": "No target object detected in the frame."}
    
    except Exception as e:
        logging.error(f"Error capturing frame: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred while capturing the frame: {e}")
    
    
        

# Example: Access the route to capture the frame and detect the object
@router.get("/capture_image")
async def capture_image(camera_id: int,of:str, target_label: str,user_id:str, db: Session = Depends(get_db)):
    return await capture_frame(camera_id,of,target_label,user_id, db)
