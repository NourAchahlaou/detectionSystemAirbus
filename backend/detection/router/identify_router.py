import asyncio

import io

from fastapi.responses import StreamingResponse
from detection.service.model_training_service import train_model
from detection.service.identifiying_service import IdentifySystem
from hardware.camera.camera import FrameSource
from api.utils.database import get_db
import time
import logging
import threading
from typing import Annotated, AsyncGenerator
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import numpy as np
import cv2


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
identify_system = IdentifySystem()



async def process_frame(frame: np.ndarray):
    """Asynchronously process a single frame to perform detection and contouring."""
    try:
        detection_results = identify_system.detect_and_contour(frame)
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
    

async def generate_frame (camera_id: int, db: Session)-> AsyncGenerator[bytes, None]:
    # Frame generation logic
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

                if frame_counter % process_interval == 0:
                    if not isinstance(frame, np.ndarray):
                        logging.error("Captured frame is not a NumPy array.")
                        continue

                    if frame.ndim != 3 or frame.dtype != np.uint8:
                        logging.error(f"Frame dimensions or data type are incorrect. Dimensions: {frame.ndim}, Data type: {frame.dtype}")
                        continue

                    processed_frame, detected_target, non_target_count = await process_frame(frame)

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

                if time.time() - detection_time > timeout_duration and not object_detected:
                    logging.debug("Timeout reached without object detection, stopping.")
                    break
            else:
                logging.debug("Camera is not running.")
                break

            await asyncio.sleep(0)  # Yield control to the event loop

    finally:
        logging.debug("Stopping frame source.")
        stop_training()
        stop_event.clear()  # Clear the event for the next use
        frame_source.stop()
        logging.debug("Stop event cleared.")




def stop_training():
    """Set the stop event to signal training to stop."""
    stop_event.set()
    logger.info("Stop training signal sent.")


        # Update the piece with the results

@router.get("/video_identify_feed")
async def video_identify_feed(camera_id: int, db: Session = Depends(get_db)):
    return StreamingResponse(generate_frame(camera_id, db), media_type='multipart/x-mixed-replace; boundary=frame')



@router.post("/stop_camera_identify_feed")
async def stop_camera_identify_feed():
    try:
        stop_training()  # Ensure this is the function to stop the feed
        return {"message": "Camera feed stopped successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
