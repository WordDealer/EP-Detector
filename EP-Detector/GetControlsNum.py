import subprocess
import time
from appium import webdriver
import cv2
import numpy as np
import  base64
import re
import os
from xml.etree import ElementTree as ET

def GetControNums(rootNode,ableCons,allCons):
    bounds = rootNode.attrib.get('bounds')
    cliAble = rootNode.attrib.get('clickable')  #clickable  scrollable
    scroAble = rootNode.attrib.get('scrollable')
    lonAble = rootNode.attrib.get('long-clickable')

    if (bounds) and (bounds not in allCons):
        allCons.append(bounds)

    if (cliAble=="true" or scroAble=="true" or lonAble=="true") and (bounds) and (bounds not in ableCons):
        ableCons.append(bounds)

    childNodes = rootNode.getchildren()

    if len(childNodes) != 0:
        for node in childNodes:
            GetControNums(node,ableCons,allCons)

fileCount = 0

def SaveConInfos(driver,appname):
    global fileCount

    try:
        image = driver.get_screenshot_as_base64()
        image = base64.b64decode(image)
        image = np.frombuffer(image, np.uint8)
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    except:
        image = None

    time.sleep(1)
    color = (0, 140, 255)

    try:
        pageSor = driver.page_source
    except:
        print('error!!')
        return


    root = ET.fromstring(pageSor)

    ableCons = []
    allCons = []

    GetControNums(root,ableCons,allCons)

    print('start')
    if type(image) == np.ndarray:
        for points in ableCons:
            nums = re.findall(r"\d+", points)
            # print(nums)
            lux = int(nums[0])
            luy = int(nums[1])
            rdx = int(nums[2])
            rdy = int(nums[3])
            cv2.rectangle(image, (lux,luy), (rdx,rdy), color, 2)

        cv2.putText(image,'ableNUm'+str(len(ableCons)),(50,100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)
        cv2.putText(image,'allNUm'+str(len(allCons)),(50,200), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)
        folder = os.path.exists(appname)
        if not folder:
            os.makedirs(appname)
        print(appname + '/the'+ str(fileCount) +'ConNumsCount.jpg')
        cv2.imwrite(appname +'/the'+ str(fileCount) +'ConNumsCount.jpg', image)
        fileCount+=1

def GetName():
    order = 'adb shell dumpsys activity activities | findstr mResumedActivity'  # 获取连接设备

    pi = subprocess.Popen(order, shell=True, stdout=subprocess.PIPE)
    subRes = pi.stdout.read().decode('utf-8').replace("\n", "").replace("\r", "")
    theee = subRes.split()
    fullName = theee[3].split('/')
    appName = fullName[0]
    actiName = fullName[1]
    if actiName[0] == '.':
        actiName = appName + actiName
    print(appName, actiName)
    return appName


if __name__ == '__main__':
    
    # Device configuration
    device_config = {
        'deviceName': '127.0.0.1:291af785',      # Device name from 'adb devices'. Examples: emulator-5554, 291af785
        'platformVersion': '11',                 # Phone version. Check: Settings -> About Phone on the device.
        'platformName': 'Android',               # Device type: iOS or Android
        'newCommandTimeout': '600'               # Timeout for new commands
    }

    driver = webdriver.Remote('http://127.0.0.1:4723/wd/hub', device_config)
    
    appname = GetName()
    key = 0

    # Keep prompting the user until they input '1'
    while key != '1':
        key = input('Continue? (Enter 1 to stop)')
        SaveConInfos(driver, appname)
