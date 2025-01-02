from pypylon import pylon
import cv2
import os
import numpy as np
import sys
from PyQt5.QtWidgets import QApplication, QInputDialog

# Initialize the application
app = QApplication(sys.argv)

# Ask the user for the reference name
reference_name, ok = QInputDialog.getText(None, "Entrez la référence", "Entrez la référence:")
if not ok or not reference_name:
    sys.exit("pas de référence. Exiting.")

# Initialize the camera
camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
camera.Open()

# Adjust camera settings
camera.Gain.Value = 0  # Set gain to 0 for lower noise
camera.ExposureTime.Value = 8000  # Increase exposure time for higher quality
camera.Gamma.Value = 2
# Set the pixel format to 16-bit grayscale if supported
if 'Mono16' in camera.PixelFormat.GetSymbolics():
    camera.PixelFormat.SetValue('Mono16')
else:
    print("16-bit format not supported. Using default format.")

# Set the camera to maximum resolution
camera.Width.Value = camera.Width.Max
camera.Height.Value = camera.Height.Max 

# Check the new settings
print(f"Resolution: {camera.Width.Value}x{camera.Height.Value}")
print(f"Pixel Format: {camera.PixelFormat.Value}")
print(f"Exposure Time: {camera.ExposureTime.Value}")
print(f"Gain: {camera.Gain.Value}")

numberOfImagesToGrab = 5000
camera.StartGrabbingMax(numberOfImagesToGrab)

# Create a named window for displaying the video
cv2.namedWindow('Video Capture', cv2.WINDOW_NORMAL)

# Initialize a counter for saved images
image_counter = 0
space_press_counter = 0
# Define the path to save images

# Create the directory if it doesn't exist

# Zoom factor (2.0 means 2x zoom)
zoom_factor = 1.0

while camera.IsGrabbing():
    grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

    if grabResult.GrabSucceeded():
        # Access the image data
        img = grabResult.Array

        # Normalize the 16-bit image for display if using 16-bit format
        if camera.PixelFormat.Value == 'Mono16':
            img = cv2.normalize(img, None, 0, 65535, cv2.NORM_MINMAX)
            img = (img / 256).astype('uint8')  # Convert to 8-bit for display

        # Digital zoom implementation
        height, width = img.shape
        center_x, center_y = width // 2, height // 2
        new_width, new_height = int(width / zoom_factor), int(height / zoom_factor)

        # Crop the region of interest (ROI) for zoom
        roi = img[center_y - new_height // 2:center_y + new_height // 2,
                  center_x - new_width // 2:center_x + new_width // 2]

        # Resize the cropped ROI back to the original image size
        zoomed_img = cv2.resize(roi, (width, height), interpolation=cv2.INTER_LINEAR)

        # Display the zoomed frame
        cv2.imshow('Video Capture', zoomed_img)

        # Check for user input to exit or take a photo
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

        elif key == ord('Z'):
            zoom_factor += 0.5
            print(zoom_factor)
        elif key == ord('z'):
            while(zoom_factor>1):
                zoom_factor -= 0.5 
                print(zoom_factor)

        # gain +/-
        elif key == ord('G'):
            camera.Gain.Value += 1
            print(f"Gain: {camera.Gain.Value}")

        elif key == ord('g'):
            while(camera.Gain.Value>1):
                camera.Gain.Value -= 1 
                print(f"Gain: {camera.Gain.Value}")

        elif key == ord('E'):
            camera.ExposureTime.Value += 1000 
            print(f"Exposure Time: {camera.ExposureTime.Value}")

        elif key == ord('e'):
            camera.ExposureTime.Value -= 1000 
            print(f"Exposure Time: {camera.ExposureTime.Value}")

        elif key == ord('A'):
            while(camera.Gamma.Value<3.5):
                camera.Gamma.Value += 0.2 
                print(camera.Gamma.Value)

        elif key == ord('a'):
            camera.Gamma.Value -= 0.2
            print(camera.Gamma.Value)

        elif key == ord(' '):  # Space bar pressed

            space_press_counter += 1

            if space_press_counter >=12:
                camera.Close()
                cv2.destroyAllWindows
                sys.exit()

            for i in range(50):
                # Randomize the settings within the given ranges
                camera.Gain.Value = np.random.uniform(0, 7)
                camera.ExposureTime.Value = np.random.uniform(3000, 12000)
                camera.Gamma.Value = np.random.uniform(0.4, 1.3)
                zoom_factor = np.random.uniform(2.0, 5.0)

                # Capture a new frame with the updated settings
                grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
                if grabResult.GrabSucceeded():
                    img = grabResult.Array

                    if camera.PixelFormat.Value == 'Mono16':
                        img = cv2.normalize(img, None, 0, 65535, cv2.NORM_MINMAX)
                        img = (img / 256).astype('uint8')

                    # Apply zoom to the new image
                    new_width, new_height = int(width / zoom_factor), int(height / zoom_factor)
                    roi = img[center_y - new_height // 2:center_y + new_height // 2,
                              center_x - new_width // 2:center_x + new_width // 2]
                    zoomed_img = cv2.resize(roi, (width, height), interpolation=cv2.INTER_LINEAR)

                    # Save the current frame as an image file
                    cv2.imwrite( zoomed_img)
                  
                    image_counter += 1

                grabResult.Release()

    grabResult.Release()

# Release resources
camera.Close()
cv2.destroyAllWindows()
