
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

if __name__ == '__main__':
    
    # Device configuration
    device_config = {
        'deviceName': '127.0.0.1:291af785',      # Device name from 'adb devices'
        'platformVersion': '11',                 # Phone version, available under: Settings -> About Phone
        'platformName': 'Android'                # Phone type: iOS or Android
    }

    # Start the server. If Appium isn't properly installed, opening Appium Desktop will also start the service.
    driver = webdriver.Remote('http://127.0.0.1:4723/wd/hub', device_config)
    
    # Command to fetch memory details
    adb_command = 'adb shell cat /proc/meminfo' 
    memory_details = extract_memory_info(adb_command)
    
    print(memory_details)


        






