import cv2
from typing import Dict, List
import win32com.client
from pypylon import pylon
import threading
import time
import numpy as np

from hardware.camera.external_camera import get_available_cameras, get_usb_devices


# Function to resize an image while maintaining aspect ratio
def resize_image(image, max_width, max_height):
    height, width = image.shape[:2]
    aspect_ratio = width / height

    if width > height:
        new_width = min(max_width, width)
        new_height = int(new_width / aspect_ratio)
    else:
        new_height = min(max_height, height)
        new_width = int(new_height * aspect_ratio)

    return cv2.resize(image, (new_width, new_height))




def initialize_camera(basler_device):
    """Initialize and configure the Basler camera."""
    camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateDevice(basler_device))
    camera.Open()
    camera.ExposureTime.SetValue(40000)
    camera.Gain.SetValue(0.8)
    camera.AcquisitionMode.SetValue("Continuous")
    return camera





def process_basler_camera(basler_device, caption):
    """Capture and display frames from a Basler camera with resizing."""
    camera = initialize_camera(basler_device)

    # Print camera details
    camera_info = camera.GetDeviceInfo()
    print("Camera Details:")
    print(f"  Model: {camera_info.GetModelName()}")
    print(f"  Manufacturer: {camera_info.GetVendorName()}")
    print(f"  Serial Number: {camera_info.GetSerialNumber()}")

    camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

    try:
        time.sleep(2)  # Allow camera to stabilize
        while camera.IsGrabbing():
            grab_result = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

            if grab_result.GrabSucceeded():
                img = grab_result.Array

                # Resize image
                resized_img = resize_image(img, max_width=1000, max_height=700)

                # Display resized image
                cv2.imshow(f"Basler Camera {caption}", resized_img)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            grab_result.Release()
    except Exception as e:
        print(f"An error occurred with Basler Camera {caption}: {e}")
    finally:
        camera.StopGrabbing()
        camera.Close()


# Main Logic
if __name__ == "__main__":
    cameras = get_available_cameras()
    print("Available Cameras:", cameras)

    threads = []

    for cam in cameras:
        if cam["type"] == "opencv":
            camera = cv2.VideoCapture(cam["index"])
            if camera.isOpened():
                thread = threading.Thread(target=process_opencv_camera, args=(camera, cam["index"]))
                threads.append(thread)
                thread.start()

        elif cam["type"] == "basler":
            thread = threading.Thread(target=process_basler_camera, args=(cam["device"], cam["caption"]))
            threads.append(thread)
            thread.start()

    for thread in threads:
        thread.join()

    cv2.destroyAllWindows()
