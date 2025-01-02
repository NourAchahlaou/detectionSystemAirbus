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


