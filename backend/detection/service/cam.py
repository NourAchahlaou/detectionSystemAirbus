import time
import cv2
import numpy as np
from pypylon import pylon

# Function to simulate zoom (crop and resize)
def simulate_zoom(image, zoom_level):
    h, w = image.shape[:2]
    crop_size = (int(w / zoom_level), int(h / zoom_level))
    x_start = (w - crop_size[0]) // 2
    y_start = (h - crop_size[1]) // 2
    cropped_img = image[y_start:y_start + crop_size[1], x_start:x_start + crop_size[0]]
    zoomed_img = cv2.resize(cropped_img, (w, h))  # Resize back to original size
    return zoomed_img

# Initialize the camera
camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())

# Open the camera
camera.Open()

# Set camera parameters
camera.ExposureTime.SetValue(40000)  # Adjust exposure time
camera.Gain.SetValue(0.8)  # Adjust gain
camera.AcquisitionMode.SetValue("Continuous")

# Start the grabbing process
camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)


# Allow the camera to stabilize
time.sleep(2)  # Give the camera time to prepare for image capture

# Grab one image with a timeout of 5000 ms (5 seconds)
grab_result = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

# Check if the image was grabbed successfully
if grab_result.GrabSucceeded():
    # If successful, get the image dimensions
    print(f"Image grabbed successfully from Basler camera, width: {grab_result.GetWidth()} height: {grab_result.GetHeight()}")

    # Convert the image to an OpenCV-compatible format (numpy array)
    img = grab_result.Array

    # Resize the image to fit the screen
    max_width = 2450
  # Maximum width for screen display
    max_height = 600  # Maximum height for screen display
    height, width = img.shape[:2]

    # Calculate the aspect ratio
    aspect_ratio = width / height

    # Calculate the new dimensions based on the screen size
    if width > height:
        new_width = min(max_width, width)
        new_height = int(new_width / aspect_ratio)
    else:
        new_height = min(max_height, height)
        new_width = int(new_height * aspect_ratio)

    resized_img = cv2.resize(img, (new_width, new_height))

    # Display the resized image
    cv2.imshow("Resized Image", resized_img)
    cv2.waitKey(0)  # Wait until a key is pressed

    # Calculate the center region to crop
    crop_size = (int(resized_img.shape[1] // 2), int(resized_img.shape[0] // 2))  # 50% of resized size
    x_start = (resized_img.shape[1] - crop_size[0]) // 2
    y_start = (resized_img.shape[0] - crop_size[1]) // 2

    # Crop the center of the resized image
    center_img = resized_img[y_start:y_start + crop_size[1], x_start:x_start + crop_size[0]]

    # Display the cropped center image
    cv2.imshow("Center Image", center_img)
    cv2.waitKey(0)  # Wait until a key is pressed



else:
    # If the image grab failed, print an error message
    print("Failed to grab image from Basler camera")

# Release the grab result and stop grabbing process
grab_result.Release()
camera.StopGrabbing()

# Close the camera
camera.Close()
