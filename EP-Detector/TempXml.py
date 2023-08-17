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
from xml.etree import ElementTree as ET

if __name__ == '__main__':
    '''Main entry point for the script. Handles device connection and captures screenshot & activity information.'''

    # Define device configuration
    desc = {
        'deviceName': '127.0.0.1:291af785',   # Device name from `adb devices`
        'platformVersion': '11',              # Device version found in: Settings -> About phone
        'platformName': 'Android'             # Device type, either iOS or Android
    }

    # Establish connection to Appium server
    driver = webdriver.Remote('http://127.0.0.1:4723/wd/hub', desc)

    # Initialize empty list for misOperations
    misOperations = []

    # Attempt to get a screenshot from the device
    try:
        image_data = driver.get_screenshot_as_base64()
        image = base64.b64decode(image_data)
        image = np.frombuffer(image, np.uint8)
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    except:
        image = None

    # Retrieve current activity name
    actiName = driver.current_activity

    # Fetch the current page's XML source
    pageSor = driver.page_source

    # Write the XML source to a file
    with open(f'the{actiName}xmlRes.xml', 'w', encoding='utf-8') as f:
        f.write(pageSor)

    # Save the screenshot as an image
    if image is not None:
        cv2.imwrite(f'the{actiName}scanRes.jpg', image)

    # Display the misOperations
    print('Misoperations:', misOperations)








