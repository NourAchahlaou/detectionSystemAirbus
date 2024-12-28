import time
import cv2
import numpy as np
from pypylon import pylon


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


# Function to crop the center region of an image
def crop_center(image, crop_width, crop_height):
    h, w = image.shape[:2]
    x_start = (w - crop_width) // 2
    y_start = (h - crop_height) // 2
    return image[y_start:y_start + crop_height, x_start:x_start + crop_width]


# Initialize and configure the camera
def initialize_camera():
    camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
    camera.Open()
    camera.ExposureTime.SetValue(40000)
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
            resized_img = resize_image(img, max_width=800, max_height=600)

            # Display the resized image
            cv2.imshow("Resized Image", resized_img)

            # Crop the center of the resized image
            center_img = crop_center(resized_img, crop_width=resized_img.shape[1] // 2,
                                     crop_height=resized_img.shape[0] // 2)

            # Display the cropped center image
            cv2.imshow("Center Image", center_img)
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
