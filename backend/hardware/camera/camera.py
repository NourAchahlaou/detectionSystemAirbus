
import os
import threading
from pypylon import pylon
from sqlalchemy import func
from typing import Dict, Generator, List, Optional, Tuple
import cv2
from fastapi import HTTPException

from sqlalchemy.orm import Session
from api.camera.models.camera_settings import UpdateCameraSettings

from database.piece.piece import Piece
from database.piece.piece_image import PieceImage
from hardware.camera.external_camera import get_available_cameras
from database.camera.camera_settings import CameraSettings
from database.camera.camera import Camera
from datetime import datetime
import asyncio
stop_event = asyncio.Event()

class FrameSource:
    """
    Allows capturing images from a camera frame-by-frame.
    """

    def __init__(self, cam_id=None,):
        self.camera_is_running = False
        self.cam_id = cam_id
        self.capture = None
        self.detection_service = None
        self.temp_photos = []  # To keep track of temporary photos
        
        self.confidence_threshold = 0.5  # Set the confidence threshold
    # Reset virtual_storage whenever needed


    def _check_camera(self):
        return self.capture.isOpened()

    def detect_and_save_cameras(self, db: Session):
        available_cameras = get_available_cameras()  # Use the updated function
        print("Available Cameras:", available_cameras)

        for camera in available_cameras:
            if camera['type'] == 'basler':
                # Handle Basler camera
                print(f"Detected Basler Camera: {camera['caption']}")
                
                # Assume `device` contains necessary Basler information
                basler_info = {
                    "type": "basler",
                    "caption": camera['caption'],
                    "device_details": str(camera['device'])  # Convert to string for saving if needed
                }
                # Pass the correct camera type and other details
                camera_info = self.get_camera_info(camera_index=None,  # Basler cameras might not use index
                                                    model_name=camera['caption'], 
                                                    camera_type='basler', 
                                                    device=camera['device'])
                if camera_info:
                    print(camera_info)
                    self.save_camera_info(db, camera_info)

            elif camera['type'] == 'opencv':
                # Handle OpenCV-compatible camera
                index = camera.get('index')
                capture = cv2.VideoCapture(index)

                if capture.isOpened():
                    print(f"Detected OpenCV Camera: {camera['caption']}")

                    # Pass the correct camera type
                    camera_info = self.get_camera_info(camera_index=index, 
                                                    model_name=camera['caption'], 
                                                    camera_type='regular')
                    if camera_info:
                        print(camera_info)
                        self.save_camera_info(db, camera_info)

                    capture.release()
                else:
                    print(f"Failed to open OpenCV Camera at index {index}")
                    continue

        return available_cameras


    @staticmethod
    def get_camera_info(camera_index: Optional[int], model_name: str, camera_type: str, device: Optional[pylon.DeviceInfo] = None) -> Optional[Dict]:
        """
        Retrieve or apply default camera settings based on the camera type (regular or Basler).
        """
        try:
            if camera_type == "regular":
                # For OpenCV-compatible cameras
                capture = cv2.VideoCapture(camera_index)
                if not capture.isOpened():
                    raise ValueError(f"Failed to open camera with index {camera_index}")

                # Getting camera settings
                settings = {
                    "exposure": capture.get(cv2.CAP_PROP_EXPOSURE),
                    "contrast": capture.get(cv2.CAP_PROP_CONTRAST),
                    "brightness": capture.get(cv2.CAP_PROP_BRIGHTNESS),
                    "focus": capture.get(cv2.CAP_PROP_FOCUS),
                    "aperture": capture.get(cv2.CAP_PROP_APERTURE),
                    "gain": capture.get(cv2.CAP_PROP_GAIN),
                    "white_balance": capture.get(cv2.CAP_PROP_WHITE_BALANCE_BLUE_U),
                }
                return {
                    "camera_type": "regular",
                    "camera_index": camera_index,
                    "model": model_name,
                    "settings": settings,
                }

            elif camera_type == "basler" and device:
                # For Basler cameras
                camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateDevice(device))
                camera.Open()

                # Get the camera's node map
                node_map = camera.GetNodeMap()

                # Apply default settings (no node checking)
                print("Applying default settings for Basler camera...")
                try:
                    exposure_node = node_map.GetNode("ExposureTime")
                    exposure_node.SetValue(40000)  # Default exposure time (in microseconds)

                    gain_node = node_map.GetNode("Gain")
                    gain_node.SetValue(0.8)  # Default gain

                    acquisition_mode_node = node_map.GetNode("AcquisitionMode")
                    acquisition_mode_node.SetValue("Continuous")  # Default acquisition mode
                except Exception as e:
                    print(f"Error applying default settings: {e}")

                # Retrieve camera settings (matching OpenCV attributes)
                settings = {
                    "exposure": 40000,  # Use default set value for ExposureTime
                    "contrast": None,  # Basler cameras don't support contrast directly
                    "brightness": None,  # Basler cameras don't support brightness directly
                    "focus": None,  # Basler cameras may not support manual focus
                    "aperture": None,  # Basler cameras may not support aperture control
                    "gain": 0.8,  # Use default set value for Gain
                    "white_balance": None,  # Basler cameras may not support white_balance directly
                }

                # Retrieve camera information
                camera_info = camera.GetDeviceInfo()
                camera.Close()

                return {
                    "camera_type": "basler",
                    "serial_number": camera_info.GetSerialNumber(),
                    "model": model_name,
                    "settings": settings,
                }

            else:
                raise ValueError(f"Unsupported camera type: {camera_type}")

        except Exception as e:
            print(f"Error retrieving camera info for {camera_type} camera: {e}")
            return None

        finally:
            if 'capture' in locals() and capture.isOpened():
                capture.release()


    @staticmethod
    def save_camera_info(db: Session, camera_info: Dict):
        """
        Save camera information into the database, handling both regular and Basler cameras.
        """
        # Check if the camera already exists
        existing_camera = db.query(Camera).filter(Camera.model == camera_info['model']).first()
        if existing_camera:
            print("Camera already registered.")
            return existing_camera

        # Create CameraSettings object
        settings = CameraSettings(
            exposure=camera_info['settings'].get('exposure'),
            contrast=camera_info['settings'].get('contrast'),
            brightness=camera_info['settings'].get('brightness'),
            focus=camera_info['settings'].get('focus'),
            aperture=camera_info['settings'].get('aperture'),
            gain=camera_info['settings'].get('gain'),
            white_balance=camera_info['settings'].get('white_balance'),
        )

        # Add settings to the database
        db.add(settings)
        db.commit()
        db.refresh(settings)

        # Create Camera object
        camera = Camera(
            camera_type=camera_info['camera_type'],
            camera_index=camera_info.get('camera_index'),  # Index for regular cameras
            model=camera_info['model'],
            status=False,
            settings_id=settings.id
        )

        # Add camera to the database
        db.add(camera)
        db.commit()   
        db.refresh(camera)

        print("Camera and settings registered successfully!")
        return camera


    def get_camera_by_index(self, camera_id, db: Session):
       
        return db.query(Camera).filter(Camera.id == camera_id).first()

    def get_camera_model_and_ids(self, db: Session) -> List[Tuple[int, str]]:

        return db.query(Camera.id, Camera.model).all()
    

    def start(self, camera_id, db: Session ):
        if self.camera_is_running:
            print("Camera is already running.")
            return

        if camera_id is None:
            raise ValueError("Please provide a camera ID to start the camera.")

        # Fetch the camera from the database using the provided ID
        camera = self.get_camera_by_index(camera_id, db)
        if camera is None:
            raise ValueError(f"No camera found with id {camera_id} in the database.")
        
        # Start the camera using the fetched index or identifier
        self.capture = cv2.VideoCapture(camera.camera_index)
        if not self._check_camera():
            raise SystemError(f"Camera with index {camera.camera_index} not working.")

        self.camera_is_running = True
        print(f"Camera with index {camera.camera_index} started successfully.")
   
 # Event to signal when to stop
    def stopInspection(self):
        if not self.camera_is_running:
            print("Camera is not running.")
            return

        if self.capture is not None:
            self.capture.release()
            self.capture = None

        self.camera_is_running = False

    #     # Set the global stop_event to signal stop
        if 'stop_event' in globals():
            stop_event.set()

    print("Camera stopped and resources released.")

    def stop(self):
        if not self.camera_is_running:
            print("Camera is not running.")
            return

        if self.capture is not None:
            self.capture.release()
            self.capture = None

        self.camera_is_running = False
        stop_event = threading.Event() 
        

      
        # Set the event to signal stop
        stop_event.set()  
        print("Camera stopped and resources released.")



    def frame(self):
        assert self.camera_is_running, "Start the camera first by calling the start() method"

        success, frame = self.capture.read()
        if not success:
            raise SystemError("Failed to capture a frame.")

        return frame

    def generate_frames(self) -> Generator[bytes, None, None]:
        assert self.camera_is_running, "Start the camera first by calling the start() method"
        while self.camera_is_running:
            success, frame = self.capture.read()
            if not success:
                break
            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    
    
# !TODO : change the timestamps into a counter 

    def next_frame(self, db: Session, save_folder: str, url: str, piece_label: str):
        assert self.camera_is_running, "Start the camera first by calling the start() method"

        # Check if the piece already exists in the database
        piece = db.query(Piece).filter(Piece.piece_label == piece_label).first()

        if piece is None:
            # If the piece doesn't exist, create a new one
            piece = Piece(piece_label=piece_label, nbre_img=0)
            db.add(piece)
            db.commit()
            db.refresh(piece)

        
        

        success, frame = self.capture.read()
        if not success:
            raise SystemError("Failed to capture a frame")

        # Resize the frame if needed
        frame = cv2.resize(frame, (1000, 1000))

        # Generate a filename based on the current time
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"{piece_label}_{timestamp}.jpg"
        file_path = os.path.join(save_folder, filename)
        photo_url = os.path.join(url, filename)  # Renamed from `url` to `photo_url` to avoid shadowing the input parameter

        # Save the frame as an image file
        cv2.imwrite(file_path, frame)
        if piece.nbre_img == 10 :
            raise SystemError("number of images has already reached 10")
        self.temp_photos.append({
            'piece_id': piece.id,
            'file_path': file_path,
            'timestamp': datetime.now()
        })
        print(len(self.temp_photos))

        # Check if the number of photos captured is equal to max_photos
        if len(self.temp_photos) == 10 and piece.nbre_img <= 10:
            print (piece.nbre_img)
            for photo in self.temp_photos:
                piece.nbre_img += 1
                # Save the file path to the database associated with the piece
                new_photo = PieceImage(piece_id=photo['piece_id'], piece_path=photo['file_path'], timestamp=photo['timestamp'], url=photo_url)
                db.add(new_photo)
                db.commit()
                db.refresh(piece)
            self.temp_photos = [] 
        else:
            print("Number of photos is not compatible with the requested number")

        print("Photo of the piece is registered successfully!")
        return frame
    

    def capture_images(self, save_folder: str, url: str, piece_label: str):
        assert self.camera_is_running, "Start the camera first by calling the start() method"
        success, frame = self.capture.read()
        if not success:
            raise SystemError("Failed to capture a frame")

        # Resize the frame if needed
        frame = cv2.resize(frame, (1000, 750))

        # Generate a filename based on the current time
        timestamp = datetime.now()
        image_count = len(self.temp_photos) + 1  # Get the current image count
        image_name = f"{piece_label}_{image_count}.jpg"  # Use the required naming format
        file_path = os.path.join(save_folder, image_name)
        photo_url = os.path.join(url, image_name) 

        # Save the frame as an image file
        cv2.imwrite(file_path, frame)

        # Store the captured photo in a temporary list
        self.temp_photos.append({
            'piece_label': piece_label,
            'file_path': file_path,
            'timestamp': timestamp,
            'url': photo_url,
            'image_name': image_name
        })

        if len(self.temp_photos) > 10:
            raise SystemError("Already 10 pictures captured.")
        
        print(f"Captured {len(self.temp_photos)} photo(s) so far.")
        return frame

    def cleanup_temp_photos(self):
        for photo in self.temp_photos:
            try:
                os.remove(photo['file_path'])
            except FileNotFoundError:
                print(f"File {photo['file_path']} not found for deletion.")
        self.temp_photos = []  # Clear the temp list
        print("Temporary photos have been cleaned up.")
    

    def save_images_to_database(self, db: Session, piece_label: str):
        # Extract the group prefix from the piece label (e.g., "D123.12345")
        group_prefix = '.'.join(piece_label.split('.')[:2])
        # Ensure the model directory exists
  
        # piece_labels = get_piece_labels_by_group(group_prefix, db)
        # print("Retrieved piece labels:", piece_labels)

        # # Rotate and save images and annotations for each piece label
        # for piece_label in piece_labels:
        #     print(piece_label)
        #     rotate_and_save_images_and_annotations(piece_label, rotation_angles=[90, 180, 270])


        # Find the maximum class_data_id 
        max_class_data_id = db.query(func.max(Piece.class_data_id)).scalar()
        
        

        if len(self.temp_photos) == 0:
            raise SystemError("There are no photos captured in the temp list.")

        # Check if the piece already exists in the database
        piece = db.query(Piece).filter(Piece.piece_label == piece_label).first()

        if piece is None:
            # If no piece exists, set class_data_id to 0; otherwise, increment max_class_data_id by 1
            next_class_data_id = (max_class_data_id + 1) if max_class_data_id is not None else 0
            
            # Create a new piece with the determined class_data_id
            piece = Piece(
                piece_label=piece_label,
                nbre_img=0,
                class_data_id=next_class_data_id
            )
            db.add(piece) 
            db.commit()
            db.refresh(piece)


        # Iterate over the list of captured photos and save them to the database
        if len(self.temp_photos) == 10 and piece.nbre_img <= 10:
            for index, photo in enumerate(self.temp_photos, start=1):
                piece.nbre_img += 1

                # Save the file path to the database associated with the piece
                new_photo = PieceImage(
                    piece_id=piece.id,
                    image_name=photo['image_name'],  # Use the formatted image name
                    piece_path=photo['file_path'],
                    timestamp=photo['timestamp'],
                    url=photo['url']
                )
                db.add(new_photo)
                db.commit()
                db.refresh(piece)

            self.temp_photos = []  # Clear the temporary list after saving

            print("All captured photos have been saved to the database.")
        else:
            print(len(self.temp_photos))
            self.temp_photos = [] 
        
            raise SystemError("Number of images has already reached 10")


 
    def get_camera(camera_id: int, db: Session):
        # Fetch the camera details
        camera = db.query(Camera).filter(Camera.id == camera_id).first()
        if not camera:
            raise HTTPException(status_code=404, detail="Camera not found")
        # Fetch the related settings
        settings = db.query(CameraSettings).filter(CameraSettings.id == camera.settings_id).all()        
        # Include settings in the camera details
        camera_data = camera.__dict__
        camera_data["settings"] = [setting.__dict__ for setting in settings]

        return camera_data
        
    @staticmethod
    def change_camera_settings(camera_id: int, camera_settings_update: UpdateCameraSettings, db: Session):
        # Fetch the camera by its ID
        camera = db.query(Camera).filter(Camera.id == camera_id).first()
        if not camera:
            raise HTTPException(status_code=404, detail="Camera not found")

        # Fetch the associated settings
        camera_settings = db.query(CameraSettings).filter(CameraSettings.id == camera.settings_id).first()
        if not camera_settings:
            raise HTTPException(status_code=404, detail="Camera settings not found")

        # Open the camera using OpenCV
        capture = cv2.VideoCapture(camera_settings.cameraIndex)
        if not capture.isOpened():
            raise HTTPException(status_code=500, detail="Failed to open camera")


        # Update the settings
        try:
            for key, value in camera_settings_update.dict(exclude_unset=True).items():
                setattr(camera_settings, key, value)

                if key == "brightness":
                    capture.set(cv2.CAP_PROP_BRIGHTNESS, value)
                elif key == "contrast":
                    capture.set(cv2.CAP_PROP_CONTRAST, value)
                elif key == "exposure":
                    capture.set(cv2.CAP_PROP_EXPOSURE, value)
                elif key == "white_balance":
                    capture.set(cv2.CAP_PROP_WHITE_BALANCE_BLUE_U, value)
                elif key == "focus":
                    capture.set(cv2.CAP_PROP_FOCUS, value)
                elif key == "aperture":
                    capture.set(cv2.CAP_PROP_APERTURE, value)
                elif key == "gain":
                    capture.set(cv2.CAP_PROP_GAIN, value)

            db.commit()
            db.refresh(camera_settings)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update camera settings: {e}")
        finally:
            capture.release()
        
        return camera   
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       