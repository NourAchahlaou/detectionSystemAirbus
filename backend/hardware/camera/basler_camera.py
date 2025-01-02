import cv2
from typing import Dict, List
import win32com.client

def get_usb_devices() -> List[Dict[str, str]]:
    wmi = win32com.client.GetObject("winmgmts:")
    devices = wmi.ExecQuery("SELECT * FROM Win32_PnPEntity WHERE Caption LIKE '%Camera%'")

    cameras = []
    for device in devices:
        cameras.append({
            "Caption": device.Caption,
            "DeviceID": device.DeviceID
        })

    return cameras




def open_camera_by_device_id(device_id):
    capture = cv2.VideoCapture(f"video={device_id}")
    if capture.isOpened():
        return capture
    else:
        return None
usb_cameras = get_usb_devices()
print(usb_cameras)
available_cameras = []    
for index, camera in enumerate(usb_cameras):
    print("enumeration", index, camera)
    capture = open_camera_by_device_id(camera['DeviceID'])
    if capture:
        available_cameras.append(camera)
        print(f"Detected Camera: {camera['Caption']}")



        capture.release()
    else:
        print(f"Not detecting any camera with DeviceID {camera['DeviceID']}")
