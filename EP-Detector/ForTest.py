
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

# from Step1Spacing import ScanPage

if __name__ == '__main__':

    desc={}

    desc['deviceName']='127.0.0.1:291af785'#手机设备名称，adb devices
    desc['platformVersion']='11'#手机版本，在手机中：设置--关于手机
    desc['platformName']='Android' #手机类型，ios或android


    #启动服务端，再cmd窗口输入appium.如果appium没有安装好，可以打开appium-desktop.也相当于启动了服务

    driver=webdriver.Remote('http://127.0.0.1:4723/wd/hub',desc)
 

    # time.sleep(1)
    order = 'adb shell cat /proc/meminfo' 
    #
    pi = subprocess.Popen(order, shell=True, stdout=subprocess.PIPE)
    subRes = pi.stdout.read().decode('utf-8').replace("\n", " ").replace("\r", " ")



    re1 = r'MemFree:(.*?)MemAvailable:'

    theee = re.findall(re1, subRes)[0].split() #[0]
    print(theee)



        






