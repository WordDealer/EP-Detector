
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

    desc={}

    desc['deviceName']='127.0.0.1:291af785'#手机设备名称，adb devices
    desc['platformVersion']='11'#手机版本，在手机中：设置--关于手机
    desc['platformName']='Android' #手机类型，ios或android


    #启动服务端，再cmd窗口输入appium.如果appium没有安装好，可以打开appium-desktop.也相当于启动了服务

    driver=webdriver.Remote('http://127.0.0.1:4723/wd/hub',desc)
 

    # time.sleep(1)
    misOperations=[]


    # image = np.zeros(0)
    try:
        image = driver.get_screenshot_as_base64()

        image = base64.b64decode(image)
        image = np.frombuffer(image,np.uint8)
        image = cv2.imdecode(image,cv2.IMREAD_COLOR)

    except:
        image = None

    actiName = driver.current_activity

    pageSor=driver.page_source
    # try:
    #     pageSor=driver.page_source
    # except:
    #     pageSor=driver.page_source


    root = ET.fromstring(pageSor)
    with open('the'+actiName+'xmlRes.xml','w',encoding='utf-8') as f:
        f.write(driver.page_source)


    cv2.imwrite('the'+actiName+'scanRes.jpg', image)



    print('misopee!',misOperations)








