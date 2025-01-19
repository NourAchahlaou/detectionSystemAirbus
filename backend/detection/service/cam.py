import time
import cv2
import numpy as np
from pypylon import pylon
import os
from datetime import datetime

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

# Function to save an image with a dynamic filename
def save_image(image):
    # Create the directory if it doesn't exist
    os.makedirs('captured_images', exist_ok=True)
    
    # Generate a dynamic filename with a timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f'captured_images/image_{timestamp}.jpg'
    
    # Save the image
    cv2.imwrite(filename, image)
    print(f"Image saved as {filename}")

# Initialize and configure the camera
def initialize_camera():
    camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
    camera.Open()
    camera.Width.SetValue(5000)
    camera.Height.SetValue(3000)
    camera.ExposureTime.SetValue(50000)
    camera.Gain.SetValue(0.8)
    camera.AcquisitionMode.SetValue("Continuous")
    return camera

def main():
    # Initialize the camera
    camera = initialize_camera()

    # Print camera details
    camera_info = camera.GetDeviceInfo()
    print("Camera Details:")
    print(f"  Model: {camera_info.GetModelName()}")
    print(f"  Manufacturer: {camera_info.GetVendorName()}")
    print(f"  Serial Number: {camera_info.GetSerialNumber()}")

    # Start grabbing images
    camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

    try:
        # Allow the camera to stabilize
        time.sleep(2)

        # Grab one image
        grab_result = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

        if grab_result.GrabSucceeded():
            print(f"\nImage grabbed successfully, width: {grab_result.GetWidth()}, height: {grab_result.GetHeight()}")

            # Convert to OpenCV format
            img = grab_result.Array

            # Resize image for display
            resized_img = resize_image(img, max_width=1920, max_height=1080)

            # Display the resized image
            cv2.imshow("Resized Image", resized_img)

            # Save the image with a dynamic name
            save_image(resized_img)

            cv2.waitKey(0)

        else:
            print("Failed to grab image from the camera.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Cleanup
        if grab_result:
            grab_result.Release()
        camera.StopGrabbing()
        camera.Close()

if __name__ == "__main__":
    main()
