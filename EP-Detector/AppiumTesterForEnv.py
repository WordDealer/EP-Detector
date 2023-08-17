import random
import re
import numpy as np
import time
import cv2
import os
import base64
from appium import webdriver
from appium.webdriver.common.touch_action import TouchAction
from appium.webdriver.common.multi_action import MultiAction
from xml.etree import ElementTree as ET
import subprocess
from behaviour import Behaviour,orderBehavList,clickActList,longClickList,downSwipeActList,otherSwipeActList
from XmlRecord import ActRecord
from Step3Enviromen import Enviromen
import json
from Timer import  TimeRecord

class TestApp:

    def __init__(self, driver, net_con="wlan", app_name=None, main_activity_name="com.yy.hiyo.MainActivity"):
        """
        Initialize TestApp class.

        Args:
        - driver: device parameters.
        - net_con: network connection type. Can be "wlan", "data", or "imitator".
        - app_name: name of the app. e.g., com.eg.android.AlipayGphone.
        - main_activity_name: name of the main activity for the app.
        """

        self.driver = driver
        self.net_con = net_con

        self.app_name = app_name
        self.main_activity_name = main_activity_name

        self.xml = None
        self.main_xml = None
        self.act_record = ActRecord()  # Records actions and activities for traversal
        self.current_actions = []  # Steps required to navigate from the main activity to the current one

        self.similarity_threshold = 0.7  # Similarity threshold for pages without interaction but with scroll bars
        self.wait_time = 2
        self.main_similarity_threshold = 0.8  # Similarity threshold for the main page with scroll bars

        self.clarity_way = 'xml'  # Options are 'pic' or 'xml'
        self.file_count = 0
        self.mistouch_threshold = 71
        self.is_continuous = True
        self.add_long_press = False  # Indicates if long press actions should be added

        self.timer = TimeRecord()

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

    def TripFinCap(self,cliX, cliY,isTrip):
        if cliX<0:
            cliX = 1
        if cliX>self.widt:
            cliX = self.widt-1
        if cliY < 0:
            cliY = 1
        if cliY > self.heit:
            cliY = self.heit - 1

        diX =cliX
        diY =cliY

        leX = diX-30
        if leX<0:
            leX = 1

        riX = diX+30
        if riX>self.widt:
            riX = self.widt-1

        diY = diY + 200
        if diY > self.heit:
            diY = self.heit - 1

        action1 = TouchAction(self.driver)
        action2 = TouchAction(self.driver)

        action1.press(x=leX,y=cliY).wait(300).move_to(x=leX,y=diY).wait(300).release() #.wait(1000)
        action2.press(x=cliX,y=cliY).wait(300).move_to(x=diX,y=diY).wait(300).release() #.wait(1000)

        multi_action = MultiAction(self.driver)
        print(type(multi_action))
        multi_action.add(action1)
        multi_action.add(action2)
        if isTrip:
            action3 = TouchAction(self.driver)        
            action3.press(x=riX,y=cliY).wait(300).move_to(x=riX,y=diY).wait(300).release()
            multi_action.add(action3)

        multi_action.perform()
        self.driver.swipe(cliX, cliY,diX,diY)

    def DoSwipe(self,cliX,cliY,dir,actype):

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

    def GetTreeAllBounds(self,rootNode, resultList):

        resId = rootNode.attrib.get('bounds')

        if resId and resId not in resultList:
            resultList.append(resId)

        childNodes = rootNode.getchildren()
        if len(childNodes) != 0:
            for node in childNodes:
                self.GetTreeAllBounds(node, resultList)

    def GetTreeAllIds(self,rootNode, resultList):

        resId = rootNode.attrib.get('bounds')

        if resId and resId not in resultList:
            resultList.append(resId)

        childNodes = rootNode.getchildren()
        if len(childNodes) != 0:
            for node in childNodes:
                self.GetTreeAllIds(node, resultList)

    def GetTreeAll(self,rootNode, level, cliresult,scrresult,lonresult,allList,fullList):

        bounds = rootNode.attrib.get('bounds')
        cliAble = rootNode.attrib.get('clickable')  
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

    def GetName(self):
        self.GetName2()

    def GetName2(self):
        '''
        Extracts the name of the connected device and its main activity.

        Attributes:
        appName (str): The name of the connected device.
        mainActiName (str): The name of the main activity.
        '''

        # Get information on the connected device
        order = 'adb shell dumpsys activity activities | findstr topResumedActivity'
        pi = subprocess.Popen(order, shell=True, stdout=subprocess.PIPE)
        
        subRes = pi.stdout.read().decode('utf-8').replace("\n", "").replace("\r", "")
        print(subRes)
        
        theee = subRes.split()
        print(theee)
        
        # Extract app name and activity name
        fullName = theee[2].split('/')
        appName = fullName[0]
        actiName = fullName[1].split("}")[0]

        # Check if the activity name starts with '.' and prepend with app name if so
        if actiName[0] == '.':
            actiName = appName + actiName

        print(appName, actiName)
        self.appName = appName
        self.mainActiName = actiName

    def TestAllPages(self):
        '''
        Test all pages for the given application.
        
        This method tries to systematically visit all app pages by simulating
        user actions and checks for any potential risks or misbehaviors.
        
        Attributes:
            appName (str): The name of the application being tested.
            mainActiName (str): The name of the main activity of the application.
            ...
        '''
        dangerAction = []

        # Ensure app name is available
        if not self.appName:
            self.GetName()

        # Create a directory for the app if it doesn't exist
        if not os.path.exists(self.appName):
            os.makedirs(self.appName)

        # Get screen dimensions
        self.heit = self.driver.get_window_size()['height']
        self.widt = self.driver.get_window_size()['width']

        # Try to terminate the app and then restart the main activity
        try:
            self.driver.terminate_app(self.appName)
        except:
            print('no need to terminate')

        self.driver.start_activity(self.appName, self.mainActiName)
        self.driver.wait_activity(self.mainActiName, 10)
        time.sleep(20)

        # Record initial state of the app (screenshot or XML based on the approach chosen)
        if self.clarriWay == 'pic':
            try:
                self.mainActiIma = self.driver.screenshot()
            except:
                self.mainActiIma = None
        else:
            try:
                self.mainActiIma = self.driver.page_source
            except:
                print('xml error')
                self.mainActiIma = None

        # Configuration of similarity parameters
        simiLarity = 0.1
        self.mainSimiLari = simiLarity - 0.05

        # Load previous test results if applicable
        isLoad = False
        if self.isConti:
            isLoad, num = self.actRecord.Load(self.appName)
            self.fileCount = num
            print('before')

        if not isLoad:
            self.actRecord.Add(self.mainActiIma, [])

        thexml, act = self.actRecord.Get()

        # Main loop to iterate over all app pages and test them
        while thexml:
            self.timer.pageStart()
            print('not start page')
            self.xml = thexml
            self.nowAct = act

            # Terminate and restart app for a fresh start
            try:
                self.driver.terminate_app(self.appName)
            except:
                print('no need to terminate')

            # Start the main activity and handle potential errors
            try:
                self.driver.start_activity(self.appName, self.mainActiName)
            except:
                print('error!!')
                # On error, press back button twice and retry
                self.driver.press_keycode(4)
                time.sleep(0.1)
                self.driver.press_keycode(4)
                self.driver.start_activity(self.appName, self.mainActiName)

            # Ensure the main activity is loaded correctly
            isStart = self.WaitMainXml(15)
            if isStart:
                print('nowact', self.nowAct)
                self.DoAct()
            else:
                print('not start', self.mainActiName)

            # Fetch the current page XML and compare with expected
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

            # Capture the state of the app after the actions
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

            # XML parsing to identify all actionable elements on the page
            root = ET.fromstring(self.trueMainImg)
            cliResultList = []
            scrResultList = []
            lonResultList = []
            allList = []
            fullList = []
            self.GetTreeAll(root, 1, cliResultList, scrResultList, lonResultList, allList, fullList)

            # Process the actionable elements and test them
            ...

            # Store the results and move on to the next page for testing
            self.actRecord.Save(self.appName, self.fileCount)
            self.timer.pageOver()
            thexml, act = self.actRecord.Get()

        # Log any dangerous actions identified during the tests
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

class YourClassName:
    def check_and_init(self):
        """
        This function checks the app's current state and initializes it if necessary.
        :return: Boolean indicating whether the initialization was successful.
        """
        # Step 1: Compare immediately without any operations to verify consistency
        now_pic = self._get_current_display()
        if self._is_same_display(now_pic, self.trueMainImg):
            print('No action:', True)
            return True

        # Attempt to exit the current page by pressing back
        self.driver.press_keycode(4)
        time.sleep(0.5)

        now_pic = self._get_current_display()
        if self._is_same_display(now_pic, self.trueMainImg):
            print('Exit action:', True)
            return True

        # If not back to the main page, try to reproduce the previous behavior
        if len(self.nowAct) > 0:
            behavior = self.nowAct[-1]
            self.do_behavior(behavior[0], behavior[1], behavior[-1])
            time.sleep(0.5)

            now_pic = self._get_current_display()
            if self._is_same_display(now_pic, self.trueMainImg):
                return True

        # Step 4: Close the app if not at the desired page
        try:
            self.driver.terminate_app(self.appName)  # Close app
        except:
            print('No need to terminate')

        # Step 5: Restart the app and verify
        self.driver.start_activity(self.appName, self.mainActiName)
        is_started = self.wait_xml(12)
        if is_started:
            self.do_action()

        now_pic = self._get_current_display()
        if is_started and self._is_same_display(now_pic, self.trueMainImg):
            return True

        if not is_started:
            print('waitxml error')
        else:
            print('check same failed')

        print('Initialization failed!')
        return False

    def _get_current_display(self):
        """Retrieve the current app display either as an image or XML."""
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

    def _is_same_display(self, first_pic, second_pic):
        """
        Compare two displays to see if they are the same.
        :param first_pic: First display (either image or XML)
        :param second_pic: Second display (either image or XML)
        :return: Boolean indicating whether the two displays are the same.
        """
        if self.clarriWay == 'pic':
            return self.compare_hist(first_pic, second_pic, self.mainSimiLari)
        else:
            return self.comp_xml(first_pic, second_pic, self.mainSimiLari)

    def init_check_page(self):
        pass
