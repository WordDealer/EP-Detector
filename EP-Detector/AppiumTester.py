import os
import json
import random
import re
import time
import subprocess
from xml.etree import ElementTree as ET
import numpy as np
import cv2
from appium import webdriver
from appium.webdriver.common.touch_action import TouchAction
from appium.webdriver.common.multi_action import MultiAction
from behaviour import Behaviour, orderBehavList, clickActList, longClickList, downSwipeActList, otherSwipeActList
from XmlRecord import ActRecord
from Step1SpaTest import Spacing
from Step2Operation import Operation
from Step3Enviromen import Enviromen
from Timer import TimeRecord


class TestApp:

    def __init__(self, driver):
        self.driver = driver
        self.net_con = "wlan"
        self.app_name = None
        self.main_activity_name = "com.yy.hiyo.MainActivity"
        self.xml = None
        self.main_xml = None
        self.act_record = ActRecord()
        self.now_act = []
        self.similarity_threshold = 0.7
        self.wait_time = 2
        self.main_similarity_threshold = 0.8
        self.clarity_way = 'xml'
        self.file_count = 0
        self.mis_touch = 71
        self.is_continue = True
        self.add_long = False
        self.timer = TimeRecord()

    def scan_page_for_elem(self, cli_result_list, scr_result_list):
        try:
            image = self.driver.get_screenshot_as_base64()
            image = base64.b64decode(image)
            image = np.fromstring(image, np.uint8)
            image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        except:
            image = None
        color = (0, 140, 255)
        space = Spacing(self)
        mis_operations = space.ScanPage(cli_result_list, scr_result_list)
        activity_name = self.driver.current_activity
        if isinstance(image, np.ndarray):
            for points in mis_operations:
                print((points[0], points[1]))
                cv2.circle(image, (points[0], points[1]), 20, color, -1)
                cv2.putText(image, 'ableNum' + str(self.able_con_num), (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)
                cv2.putText(image, 'allNum' + str(self.all_con_num), (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)
            cv2.imwrite(f'{self.app_name}/the{activity_name}{self.file_count}scanRes.jpg', image)
            self.file_count += 1
        with open(f'{self.app_name}/the{activity_name}{self.file_count}OpeMis.txt', "w", encoding="utf-8") as file:
            file_data = json.dumps(mis_operations)
            file.write(file_data)

    def getHistSimiLari(self, stdimg, ocimg):
        if self.clarriWay == 'pic':
            if not (stdimg and ocimg):
                return -1
            stdimg = np.float32(stdimg)
            ocimg = np.float32(ocimg)
            stdimg = np.ndarray.flatten(stdimg)
            ocimg = np.ndarray.flatten(ocimg)
            imgocr = np.corrcoef(stdimg, ocimg)
            return imgocr[0, 1]
        else:
            firRoot = ET.fromstring(stdimg)
            secRoot = ET.fromstring(ocimg)
            firIdList = []
            secIdList = []    
            self.GetTreeAllIds(firRoot,firIdList)
            self.GetTreeAllIds(secRoot,secIdList)
            saNum = 0
            diNum = 0
            for firId in firIdList:
                if firId in secIdList:
                    saNum += 1
                else:
                    diNum += 1 
            for secId in secIdList:
                if secId in firIdList:
                    saNum += 1
                else:
                    diNum += 1         
            if saNum == 0:
                return 0.1
            return diNum*1.0/saNum+0.05

    def DoAct(self):

        for behav in self.nowAct:
            self.DoBehav(behav[0], behav[1],behav[-1])
            print('beh',behav)

    def DoBehav(self,cliX,cliY,behav):
        if behav == Behaviour.click:
            self.driver.tap([(cliX, cliY)])
        elif behav == Behaviour.tripleSwipe:
            self.TripFinCap(cliX,cliY,True)
        elif behav == Behaviour.doubleSwipe:
            self.TripFinCap(cliX,cliY,False)
        elif behav == Behaviour.doubleClick:
            self.driver.tap([(cliX,cliY)])
            time.sleep(0.1)
            self.driver.tap([(cliX,cliY)])
            time.sleep(1.5)
        elif behav == Behaviour.noneBehaviour:
            pass
        elif behav == Behaviour.misDoubleClick1:
            self.driver.tap([(cliX,cliY)])
            time.sleep(0.1)
            self.driver.tap([(cliX,cliY)],300)
            time.sleep(1.5)
        elif behav == Behaviour.misDoubleClick2:
            self.driver.tap([(cliX,cliY)],300)
            time.sleep(0.1)
            self.driver.tap([(cliX,cliY)])
            time.sleep(1.5)
        elif behav == Behaviour.longClick:
            self.driver.tap([(cliX,cliY)],800)
        elif behav ==Behaviour.leftSwipe:
            self.DoSwipe(cliX, cliY,"left","swip")
        elif behav == Behaviour.rightSwipe:
            self.DoSwipe(cliX, cliY,"right","swip")
        elif behav == Behaviour.upSwipe:
            self.DoSwipe(cliX, cliY,"up","swip")
        elif behav == Behaviour.downSwipe:
            self.DoSwipe(cliX, cliY,"down","swipe")
        elif behav ==Behaviour.leftScroll:
            self.DoSwipe(cliX, cliY,"left","scroll")
        elif behav == Behaviour.rightScroll:
            self.DoSwipe(cliX, cliY,"right","scroll")
        elif behav == Behaviour.upScroll:
            self.DoSwipe(cliX, cliY,"up","scroll")
        elif behav == Behaviour.downScroll:
            self.DoSwipe(cliX, cliY,"down","scroll")
        elif behav == Behaviour.misLongClick1:
            self.driver.tap([(cliX,cliY)])
            time.sleep(0.1)
            self.driver.tap([(cliX,cliY)],800)
        elif behav == Behaviour.misLongClick2:
            self.driver.tap([(cliX,cliY)],200)
        elif behav ==Behaviour.misLeftSwipe:
            self.driver.tap([(cliX,cliY)])
            time.sleep(0.1)
            self.DoSwipe(cliX, cliY,"left","swip")
        elif behav == Behaviour.misRightSwipe:
            self.driver.tap([(cliX,cliY)])
            time.sleep(0.1)
            self.DoSwipe(cliX, cliY,"right","swip")
        elif behav == Behaviour.misUpSwipe:
            self.driver.tap([(cliX,cliY)])
            time.sleep(0.1)
            self.DoSwipe(cliX, cliY,"up","swip")
        elif behav == Behaviour.misDownSwipe:
            self.driver.tap([(cliX,cliY)])
            time.sleep(0.1)
            self.DoSwipe(cliX, cliY,"down","swipe")
        elif behav ==Behaviour.misLeftScroll1:
            self.driver.tap([(cliX,cliY)])
            time.sleep(0.1)   
            self.DoSwipe(cliX, cliY,"left","scroll")
        elif behav == Behaviour.misRightScroll1:
            self.driver.tap([(cliX,cliY)])
            time.sleep(0.1)   
            self.DoSwipe(cliX, cliY,"right","scroll")
        elif behav == Behaviour.misUpScroll1:
            self.driver.tap([(cliX,cliY)])
            time.sleep(0.1)   
            self.DoSwipe(cliX, cliY,"up","scroll")
        elif behav == Behaviour.misDownScroll1:
            self.driver.tap([(cliX,cliY)])
            time.sleep(0.1)      
            self.DoSwipe(cliX, cliY,"down","scroll")
        elif behav ==Behaviour.misLeftScroll2:  
            self.DoMisScroll2(cliX, cliY,"left","scroll")
        elif behav == Behaviour.misRightScroll2:
            self.DoMisScroll2(cliX, cliY,"right","scroll")
        elif behav == Behaviour.misUpScroll2:
            self.DoMisScroll2(cliX, cliY,"up","scroll")
        elif behav == Behaviour.misDownScroll2:
            self.DoMisScroll2(cliX, cliY,"down","scroll")
        elif behav ==Behaviour.misLeftScroll3:  
            self.DoMisScroll3(cliX, cliY,"left",3)
        elif behav == Behaviour.misRightScroll3:
            self.DoMisScroll3(cliX, cliY,"right",3)
        elif behav == Behaviour.misUpScroll3:
            self.DoMisScroll3(cliX, cliY,"up",3)
        elif behav == Behaviour.misDownScroll3:
            self.DoMisScroll3(cliX, cliY,"down",3)
        elif behav ==Behaviour.misLeftScroll4:  
            self.DoMisScroll3(cliX, cliY,"left",4)
        elif behav == Behaviour.misRightScroll4:
            self.DoMisScroll3(cliX, cliY,"right",4)
        elif behav == Behaviour.misUpScroll4:
            self.DoMisScroll3(cliX, cliY,"up",4)
        elif behav == Behaviour.misDownScroll4:
            self.DoMisScroll3(cliX, cliY,"down",4)
        elif behav ==Behaviour.misLeftScroll5:  
            self.DoMisScroll3(cliX, cliY,"left",5)
        elif behav == Behaviour.misRightScroll5:
            self.DoMisScroll3(cliX, cliY,"right",5)
        elif behav == Behaviour.misUpScroll5:
            self.DoMisScroll3(cliX, cliY,"up",5)
        elif behav == Behaviour.misDownScroll5:
            self.DoMisScroll3(cliX, cliY,"down",5)

    def DoMisScroll2(self,cliX,cliY,dir,actype):
        if cliX<0:
            cliX = 1
        if cliX>self.widt:
            cliX = self.widt-1
        if cliY < 0:
            cliY = 1
        if cliY > self.heit:
            cliY = self.heit - 1
        offsetPix = 200
        if actype=="scroll":
            offsetPix = 1500
        diX =cliX
        diY =cliY
        if dir == 'left':
            diX = diX-offsetPix
            if diX<0:
                diX = 1
        elif dir =='right':
            diX = diX+offsetPix
            if diX>self.widt:
                diX = self.widt-1
        elif dir == 'up':
            diY = diY - offsetPix
            if diY < 0:
                diY = 1
        else:
            diY = diY + offsetPix
            if diY > self.heit:
                diY = self.heit - 1
        if actype == "swipe":
            self.driver.swipe(cliX, cliY,diX,diY)
        else:
            self.driver.swipeAndHold(cliX, cliY,diX,diY,200)
        time.sleep(0.1) 
        self.driver.tap([(diX,diY)],500)

    def DoMisScroll3(self,cliX,cliY,dir,actype,misType):
        if cliX<0:
            cliX = 1
        if cliX>self.widt:
            cliX = self.widt-1
        if cliY < 0:
            cliY = 1
        if cliY > self.heit:
            cliY = self.heit - 1
        offsetPix = 200
        if actype=="scroll":
            offsetPix = 1500
        diX =cliX
        diY =cliY
        if dir == 'left':
            diX = diX-offsetPix
            if diX<0:
                diX = 1
        elif dir =='right':
            diX = diX+offsetPix
            if diX>self.widt:
                diX = self.widt-1
        elif dir == 'up':
            diY = diY - offsetPix
            if diY < 0:
                diY = 1
        else:
            diY = diY + offsetPix
            if diY > self.heit:
                diY = self.heit - 1
        midX = int((diX+diX)*0.5)
        midY = int((diY+diY)*0.5)
        if misType == 3:
            self.driver.swipeAndHold(cliX, cliY,midX,midY,100)
            self.driver.tap([(midX,midY)],500)
            self.driver.swipeAndHold(midX, midY,diX,diY,100)
        elif misType ==4:
            self.driver.swipe(cliX, cliY,midX,midY)
            time.sleep(0.1)
            self.driver.swipeAndHold(midX, midY,diX,diY,100)
        else:
            self.driver.swipeAndHold(cliX, cliY,midX,midY,100)
            time.sleep(0.1)
            self.driver.swipeAndHold(midX, midY,diX,diY,100)

def TripFinCap(self, cliX, cliY, isTrip):
    """
    Perform multi-touch actions based on the given coordinates and flag.

    Args:
    cliX: Initial X-coordinate.
    cliY: Initial Y-coordinate.
    isTrip: Flag to decide if a third touch action should be executed.

    Returns:
    None
    """
    # Adjust coordinates to valid range
    if cliX < 0:
        cliX = 1
    if cliX > self.widt:
        cliX = self.widt - 1
    if cliY < 0:
        cliY = 1
    if cliY > self.heit:
        cliY = self.heit - 1

    diX = cliX
    diY = cliY

    leX = diX - 30
    if leX < 0:
        leX = 1
    riX = diX + 30
    if riX > self.widt:
        riX = self.widt - 1

    diY = diY + 200
    if diY > self.heit:
        diY = self.heit - 1

    action1 = TouchAction(self.driver)
    action2 = TouchAction(self.driver)
    action1.press(x=leX, y=cliY).wait(300).move_to(x=leX, y=diY).wait(300).release()
    action2.press(x=cliX, y=cliY).wait(300).move_to(x=diX, y=diY).wait(300).release()

    # Create a multi-touch action object
    multi_action = MultiAction(self.driver)
    print(type(multi_action))

    # Execute both action1 and action2 simultaneously
    multi_action.add(action1)
    multi_action.add(action2)
    if isTrip:
        action3 = TouchAction(self.driver)
        action3.press(x=riX, y=cliY).wait(300).move_to(x=riX, y=diY).wait(300).release()
        multi_action.add(action3)

    # Execute multi-touch actions
    multi_action.perform()
    self.driver.swipe(cliX, cliY, diX, diY)

def DoSwipe(self, cliX, cliY, dir, actype):
    """
    Perform swipe or scroll action based on the given coordinates, direction, and action type.

    Args:
    cliX: Initial X-coordinate.
    cliY: Initial Y-coordinate.
    dir: Direction for the swipe action ('left', 'right', 'up', 'down').
    actype: Type of the action to be performed ('swipe' or 'scroll').

    Returns:
    None
    """
    # Adjust coordinates to valid range
    if cliX < 0:
        cliX = 1
    if cliX > self.widt:
        cliX = self.widt - 1
    if cliY < 0:
        cliY = 1
    if cliY > self.heit:
        cliY = self.heit - 1

    offsetPix = 200
    if actype == "scroll":
        offsetPix = 1500

    diX = cliX
    diY = cliY

    # Adjust coordinates based on direction
    if dir == 'left':
        diX = diX - offsetPix
        if diX < 0:
            diX = 1
    elif dir == 'right':
        diX = diX + offsetPix
        if diX > self.widt:
            diX = self.widt - 1
    elif dir == 'up':
        diY = diY - offsetPix
        if diY < 0:
            diY = 1
    else:
        diY = diY + offsetPix
        if diY > self.heit:
            diY = self.heit - 1

    # Execute swipe or swipe and hold action based on actype
    if actype == "swipe":
        self.driver.swipe(cliX, cliY, diX, diY)
    else:
        self.driver.swipeAndHold(cliX, cliY, diX, diY, 200)

    def GetTreeAllBounds(self,rootNode, resultList):
        resId = rootNode.attrib.get('bounds')
        if resId and resId not in resultList:
            resultList.append(resId)
        childNodes = rootNode.getchildren()
        if len(childNodes) != 0:
            for node in childNodes:
                self.GetTreeAllBounds(node, resultList)

    def GetTreeAllIds(self,rootNode, resultList):
        resId = rootNode.attrib.get('bounds')  #resource-id
        if resId and resId not in resultList:
            resultList.append(resId)
        childNodes = rootNode.getchildren()
        if len(childNodes) != 0:
            for node in childNodes:
                self.GetTreeAllIds(node, resultList)

    def GetTreeAll(self,rootNode, level, cliresult,scrresult,lonresult,allList,fullList):
        bounds = rootNode.attrib.get('bounds')
        cliAble = rootNode.attrib.get('clickable')  #clickable  scrollable
        scroAble = rootNode.attrib.get('scrollable')
        lonAble = rootNode.attrib.get('long-clickable')  
        showAble = rootNode.attrib.get('displayed') 

        if (bounds) and (bounds not in fullList):
            fullList.append(bounds)

        if (cliAble=="true" or scroAble=="true" or lonAble=="true") and showAble=="true" and (bounds) and (bounds not in allList):
            allList.append(bounds)
            if lonAble == "true":
                lonresult.append(bounds)
            elif cliAble=="true" :
                cliresult.append(bounds)
            if scroAble=="true" :
                scrresult.append(bounds)       

        childNodes = rootNode.getchildren()
        if len(childNodes) != 0:
            for node in childNodes:
                self.GetTreeAll(node, level + 1, cliresult,scrresult,lonresult,allList,fullList)

    def AfterGetTreeAddClick(self,rootNode, cliresult,allList,othcliresult,repeatLi):
        bounds = rootNode.attrib.get('bounds')

        if (bounds) and (bounds not in othcliresult) and (self.IsSmallBounds(bounds,allList)):
            othcliresult.append(bounds)

        childNodes = rootNode.getchildren()
        if len(childNodes) != 0:
            for node in childNodes:
                self.AfterGetTreeAddClick(node, cliresult,allList,othcliresult,repeatLi)

    def IsSmallBounds(self,bounds,allList):
        nums = re.findall(r"\d+", bounds)
        lux = int(nums[0])
        luy = int(nums[1])
        rdx = int(nums[2])
        rdy = int(nums[3])

        for bd in allList:
            if(lux==bd[0] and rdx==bd[2] and luy==bd[1] and rdy==bd[3]):
                continue
            if(lux<=bd[0] and rdx>=bd[2] and luy<=bd[1] and rdy>=bd[3]):
                return False
        return True

    def compXml(self,firXml,secXml,simi=0.1):
        firRoot = ET.fromstring(firXml)
        secRoot = ET.fromstring(secXml)
        firIdList = []
        secIdList = []
        self.GetTreeAllIds(firRoot,firIdList)
        self.GetTreeAllIds(secRoot,secIdList)

        saNum = 0
        diNum = 0
        for firId in firIdList:
            if firId in secIdList:
                saNum += 1
            else:
                diNum += 1 
        for secId in secIdList:
            if secId in firIdList:
                saNum += 1
            else:
                diNum += 1         
        if saNum == 0:
            return False

        print('diNum*1.0/saNum',diNum,saNum)
        return (diNum*1.0/saNum)<simi

    def compXmlBounds(self,firXml,secXml,simi=0.1):
        firRoot = ET.fromstring(firXml)
        secRoot = ET.fromstring(secXml)
        firIdList = []
        secIdList = []
        self.GetTreeAllBounds(firRoot,firIdList)
        self.GetTreeAllBounds(secRoot,secIdList)
        saNum = 0
        diNum = 0

        for firId in firIdList:
            if firId in secIdList:
                saNum += 1
            else:
                diNum += 1 

        for secId in secIdList:
            if secId in firIdList:
                saNum += 1
            else:
                diNum += 1         
        
        if saNum == 0:
            return False
        print('diNum*1.0/saNum',diNum,saNum)
        return (diNum*1.0/saNum)<simi

    def WaitMainXml(self, timeout=10):

        deadline = time.time() + timeout
        while time.time() < deadline:
            current_xml = self.driver.page_source
            if self.compXml(current_xml,self.mainActiIma,0.05):
                return True
            time.sleep(.5)
        return False

    def TestBoundsAllPagesEnviron(self,pageSor):

        misOperations = []
        try:
            image = self.driver.get_screenshot_as_base64()
            image = base64.b64decode(image)
            image = np.fromstring(image,np.uint8)
            image = cv2.imdecode(image,cv2.IMREAD_COLOR)
        except:
            image = None
        color = (140, 0, 255)
        enviro = Enviromen(self)

        for bound in pageSor:
            self.timer.conStart()

            misOp = enviro.TestOneBoundAllPagesInEnviron( bound)
            misOperations.extend(misOp)
            self.timer.conOver()

        actiName = self.driver.current_activity
        print(misOperations)
        print('start')
        if type(image)==np.ndarray:
            for points in misOperations:
                print((points[0], points[1]))
                cv2.circle(image, (points[0], points[1]), 20, points[2], -1)   
                cv2.putText(image,'ableNUm'+str(self.ableConNum),(50,100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)
                cv2.putText(image,'allNUm'+str(self.allConNum),(50,200), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)

            cv2.imwrite(self.appName+'/the'+actiName+str(self.fileCount)+'enviroRes.jpg', image)
            self.fileCount += 1
        print('misopee!',misOperations)

        with  open(self.appName+'/the'+actiName+str(self.fileCount)+"Evi.txt", "w", encoding="utf-8") as file:
            fileData = json.dumps(misOperations)
            file.write(fileData)
            file.close()

        return misOperations

    def TestBoundsAllPagesMuiltActs(self, cliBoundsList,scrBoundsList,lonBoundsList):  # ,behavNum
        misOperations=[]
        # image = np.zeros(0)
        try:
            image = self.driver.get_screenshot_as_base64()
            image = base64.b64decode(image)
            image = np.fromstring(image,np.uint8)
            image = cv2.imdecode(image,cv2.IMREAD_COLOR)
        except:
            image = None
        color = (255, 140,0 )
        behavList = []
        operator = Operation(self)

        for bound in cliBoundsList:
            self.timer.conStart()
            for behavList in [clickActList]:
                misOp = operator.TestOneBoundAllPagesCompareActList( bound, behavList,False)
                misOperations.extend(misOp)
            self.timer.conOver()

        for bound in lonBoundsList:
            self.timer.conStart()
            for behavList in [longClickList]:
                misOp = operator.TestOneBoundAllPagesCompareActList( bound, behavList,False)
                misOperations.extend(misOp)

            self.timer.conOver()

        for bound in scrBoundsList:
            self.timer.conStart()
            for behavList in [downSwipeActList,otherSwipeActList]:
                misOp = operator.TestOneBoundAllPagesCompareActList( bound, behavList,False)
                misOperations.extend(misOp)
            self.timer.conOver()
        actiName = self.driver.current_activity
        print(misOperations)
        print('start')
        if type(image)==np.ndarray:
            for points in misOperations:
                print((points[0], points[1]))
                cv2.circle(image, (points[0], points[1]), 20, color, -1)   
                cv2.putText(image,'ableNUm'+str(self.ableConNum),(50,100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)
                cv2.putText(image,'allNUm'+str(self.allConNum),(50,200), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)
            cv2.imwrite(self.appName+'/the'+actiName+str(self.fileCount)+'.jpg', image)
            self.fileCount += 1

        print('misopee!',misOperations)
        storOp=[]
        for ope in misOperations:
            storOp.append((ope[0],ope[1],ope[2].value))

        with  open(self.appName+'/the'+actiName+str(self.fileCount)+"OpeMis.txt", "w", encoding="utf-8") as file:
            fileData = json.dumps(storOp)
            file.write(fileData)
            file.close()

def GetName(self):
    """
    Fetch and set the application's name and main activity name from the connected device.

    Args:
    None

    Returns:
    None
    """
    # Execute the adb command to get the name of the top resumed activity
    order = 'adb shell dumpsys activity activities | findstr topResumedActivity'
    pi = subprocess.Popen(order, shell=True, stdout=subprocess.PIPE)
    subRes = pi.stdout.read().decode('utf-8').replace("\n", "").replace("\r", "")
    print(subRes)
    theee = subRes.split()
    print(theee)
    fullName = theee[3].split('/')
    appName = fullName[0]
    actiName = fullName[1]

    # If activity name starts with '.', prepend it with the app name
    if actiName[0] == '.':
        actiName = appName + actiName

    print(appName, actiName)

    # Set the class attributes
    self.appName = appName
    self.mainActiName = actiName

def GetName2(self):
    """
    Fetch and set the application's name and main activity name from the connected device using an alternative method.

    Args:
    None

    Returns:
    None
    """
    # Execute the adb command to get the name of the top resumed activity
    order = 'adb shell dumpsys activity activities | findstr topResumedActivity'
    pi = subprocess.Popen(order, shell=True, stdout=subprocess.PIPE)
    subRes = pi.stdout.read().decode('utf-8').replace("\n", "").replace("\r", "")
    print(subRes)
    theee = subRes.split()
    print(theee)
    fullName = theee[2].split('/')
    appName = fullName[0]
    actiName = fullName[1].split("}")[0]

    # If activity name starts with '.', prepend it with the app name
    if actiName[0] == '.':
        actiName = appName + actiName

    print(appName, actiName)

    # Set the class attributes
    self.appName = appName
    self.mainActiName = actiName

    def TestAllPages(self):
        """
        Tests all pages of the given application.

        Args:
        None

        Returns:
        None
        """
        dangerAction = []

        if not self.appName:
            self.GetName2()

        folder = os.path.exists(self.appName)
        if not folder:
            os.makedirs(self.appName)

        self.heit = self.driver.get_window_size()['height'] 
        self.widt = self.driver.get_window_size()['width'] 

        try:
            self.driver.terminate_app(self.appName) # Close the app
        except:
            print('no need to terminate')
        self.driver.start_activity(self.appName, self.mainActiName)  # Try to go back to the main screen

        self.driver.wait_activity(self.mainActiName, 10) # Wait for the main screen to load (useful for skipping ads)
        time.sleep(20)

        if self.clarriWay == 'pic':
            try:
                self.mainActiIma = self.driver.screenshot()
            except:
                self.mainActiIma = None
        else:
            try:
                self.mainActiIma = self.driver.page_source
                print(self.mainActiIma)
            except:
                print('xml error')
                self.mainActiIma = None

        simiLarity = 0.1
        self.mainSimiLari = simiLarity - 0.05

        isLoad = False

        if self.isConti:  # Load the previous content
            isLoad, num = self.actRecord.Load(self.appName)
            self.fileCount = num
            print('before')
        if not isLoad:
            self.actRecord.Add(self.mainActiIma, [])
                
        thexml, act = self.actRecord.Get()

        while thexml:
            self.timer.pageStart()
            print('not start page')
            self.xml = thexml
            self.nowAct = act

            try:
                self.driver.terminate_app(self.appName) # Close the app
            except:
                print('no need to terminate')

            try:
                self.driver.start_activity(self.appName, self.mainActiName)  # Try to go back to the main screen
            except:
                print('error!!')
                self.driver.press_keycode(4)
                time.sleep(0.1)
                self.driver.press_keycode(4)
                self.driver.start_activity(self.appName, self.mainActiName)  # Try again

            isStart = self.WaitMainXml(15)

            if isStart:
                print('nowact', self.nowAct)
                print('doact')
                self.DoAct()
            else:
                print('not start', self.mainActiName)

            try:
                nowXml = self.driver.page_source
            except:
                print('get pagesource error!')
                thexml, act = self.actRecord.Get()
                continue

            if not self.compXml(nowXml, self.xml, 0.1):
                print('now', len(nowXml), 'acti', len(self.xml))
                print('goto acti with act error!')
                thexml, act = self.actRecord.Get()
                continue
            else:
                print('goto next acti!', len(self.xml))

            if self.clarriWay == 'pic':
                try:
                    self.trueMainImg = self.driver.screenshot()
                except:
                    self.trueMainImg = None
            else:
                try:
                    self.trueMainImg = self.driver.page_source
                except:
                    self.trueMainImg = None

            self.simiLari = 0.13
            if self.simiLari > 0.3:
                print('simiError!', self.simiLari)

            root = ET.fromstring(self.trueMainImg)

            # Lists to store the results
            cliResultList, scrResultList, lonResultList, allList, fullList = [], [], [], [], []

            self.GetTreeAll(root, 1, cliResultList, scrResultList, lonResultList, allList, fullList)  # Get all elements from the screen

            self.allConNum = len(fullList)
            self.ableConNum = len(allList)

            numAllList = [list(map(int, re.findall(r"\d+", bd))) for bd in fullList]

            if len(clickActList) < 5:
                otherClResultList, repeatLi = [], []
                self.AfterGetTreeAddClick(root, cliResultList, numAllList, otherClResultList, repeatLi)

                print('otherClResultList', otherClResultList)
                otherCliList, otherLonList = self.CheckOther(otherClResultList)
                cliResultList.extend(otherCliList)
                lonResultList.extend(otherLonList)

            print('cliResultList', cliResultList)
            self.ScanPageForElem(cliResultList, scrResultList)
            self.TestBoundsAllPagesMuiltActs(cliResultList, scrResultList, lonResultList)

            allOpeAbleList = cliResultList + lonResultList
            EnMisOp = self.TestBoundsAllPagesEnviron(allOpeAbleList)
            self.actRecord.SaveEnvirEP(EnMisOp)

            self.actRecord.Save(self.appName, self.fileCount)
            self.timer.pageOver()
            thexml, act = self.actRecord.Get()

        print('dangerAction', dangerAction)

        with open("dangerAction.txt", "w", encoding="utf-8") as file:
            file.write(str(dangerAction))

        self.timer.appOver(self.appName)
        self.actRecord.Save(self.appName, self.fileCount)

    def CheckOther(self,otherClResultList):
        newCliList = []
        newLonList = []
        for bd in otherClResultList:
            if self.CheckAble(bd,Behaviour.click):
                newCliList.append(bd)
            if self.addLong and self.CheckAble(bd,Behaviour.longClick):
                newLonList.append(bd)

        return newCliList,newLonList


    def CheckAble(self, bound,tempBeh):
        self.CheckAndInit()
        if self.clarriWay == 'pic':
            try:
                preActImg = self.driver.screenshot()
            except:
                preActImg = None
        else:
            try:
                preActImg = self.driver.page_source
            except:
                preActImg = None

        nums = re.findall(r"\d+", bound)
        lux = int(nums[0])
        luy = int(nums[1])
        rdx = int(nums[2])
        rdy = int(nums[3])
        midX = int((lux + rdx) * 0.5)
        midY = int((luy + rdy) * 0.5)

        cliX = midX
        cliY = midY

        if cliX < 0:
            cliX = 1
        if cliX > self.widt:
            cliX = self.widt - 1
        if cliY < 0:
            cliY = 1
        if cliY > self.heit:
            cliY = self.heit - 1

        self.DoBehav(cliX, cliY, tempBeh)
        time.sleep(0.2)

        if self.clarriWay == 'pic':
            try:
                fir_cli_CenterImg = self.driver.screenshot()
            except:
                fir_cli_CenterImg = None
        else:
            try:
                fir_cli_CenterImg = self.driver.page_source
            except:
                fir_cli_CenterImg = None

        if (self.CheckIsSame(fir_cli_CenterImg, preActImg, self.mainSimiLari)):
            return False
        else:
            return True

    def WaitXml(self, timeout=10):
        deadline = time.time() + timeout
        while time.time() < deadline:
            current_xml = self.driver.page_source
            if self.compXml(current_xml, self.mainActiIma, 0.05):
                return True
            time.sleep(.5)
        return False

def CheckAndInit(self):
    # Check at first step without any action
    nowPic = self._get_picture_or_source()

    result = self.CheckIsSame(nowPic, self.trueMainImg, self.mainSimiLari)
    print('no act:', result)
    if result:
        return True

    self.driver.press_keycode(4)
    time.sleep(0.5)

    nowPic = self._get_picture_or_source()
    result = self.CheckIsSame(nowPic, self.trueMainImg, self.mainSimiLari)
    print('exit act:', result)
    if result:
        return True

    if self.CheckIsSame(nowPic, self.trueMainImg, self.mainSimiLari):
        return True

    if len(self.nowAct) > 0:
        behav = self.nowAct[-1]
        self.DoBehav(behav[0], behav[1], behav[-1])
        time.sleep(0.5)

        nowPic = self._get_picture_or_source()
        if self.CheckIsSame(nowPic, self.trueMainImg, self.mainSimiLari):
            return True

    # Close the app if there's no match or unable to skip ad page
    self._terminate_and_restart_app()

    nowPic = self._get_picture_or_source()
    print('checktrueMain', self.compXml(self.mainActiIma, self.trueMainImg))

    if self.CheckIsSame(nowPic, self.trueMainImg, self.mainSimiLari):
        return True

    print('Initialization failed!')
    return False

def _get_picture_or_source(self):
    if self.clarriWay == 'pic':
        try:
            return self.driver.screenshot()
        except:
            return None
    else:
        try:
            return self.driver.page_source
        except:
            return None

def _terminate_and_restart_app(self):
    try:
        self.driver.terminate_app(self.appName) # Close app
    except:
        print('No need to terminate')

    self.driver.start_activity(self.appName, self.mainActiName) 
    isStart = self.WaitXml(12)
    if isStart:
        self.DoAct()
    elif not isStart:
        print('waitxml error')
    else:
        print('Check failed')

    def CheckIsSame(self,firPic,secPic,simi):
        if self.clarriWay == 'pic':
            return self.compareHist(firPic,secPic,simi)
        else:
            return self.compXml(firPic,secPic,simi)

    def InitCheckPage(self):
        pass