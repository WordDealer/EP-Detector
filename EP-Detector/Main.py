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
from behaviour import Behaviour

if __name__ == '__main__':

    # Device description
    desc = {
        'deviceName': '127.0.0.1:69abe452',   # Device name (e.g., emulator-5554, 291af785 from 'adb devices')
        'platformVersion': '13',              # Phone version (found in: Settings -> About Phone on device)
        'platformName': 'Android'             # Device type (iOS or Android)
    }

    # Initialize the webdriver
    driver = webdriver.Remote('http://127.0.0.1:4723/wd/hub', desc)

    # Testing the application's pages
    test = TestApp(driver)
    test.TestAllPages()

    print("Main finished")
