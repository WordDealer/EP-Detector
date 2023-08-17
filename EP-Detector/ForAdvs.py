
import time
from appium import webdriver
from appium.webdriver.common.touch_action import TouchAction
from appium.webdriver.common.multi_action import MultiAction
import cv2
import numpy as np
from AppiumTester import  TestApp
import base64
import subprocess
import re
from Step1SpaTest import Spacing

if __name__ == '__main__':
    
    # Device configurations
    desc = {
        'deviceName': '127.0.0.1:69abe452',  # Device name, from adb devices
        'platformVersion': '11',  # Phone version, can be found in phone settings
        'platformName': 'Android'  # Phone type, can be iOS or Android
    }

    # Start the server. Use cmd to enter 'appium'. 
    # If appium is not set up, open appium-desktop. It also starts the service.
    driver = webdriver.Remote('http://127.0.0.1:4723/wd/hub', desc)

    misOperations = []
    image = None
    
    try:
        # Get screenshot in base64 format
        screenshot = driver.get_screenshot_as_base64()
        image = base64.b64decode(screenshot)
        image = np.frombuffer(image, np.uint8)
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    except Exception as e:
        print(f"Error: {e}")

    color = (0, 140, 255)
    pageSource = driver.page_source

    # Scan the current page for misoperations
    misOperations = ScanPage(71, pageSource)

    print(misOperations)
    print('Start processing image...')
    if isinstance(image, np.ndarray):
        for points in misOperations:
            print((points[0], points[1]))
            cv2.circle(image, (points[0], points[1]), 20, color, -1)
        
        activity_name = driver.current_activity
        cv2.imwrite(f'the_{activity_name}_scanRes.jpg', image)
    print('Misoperations found:', misOperations)







