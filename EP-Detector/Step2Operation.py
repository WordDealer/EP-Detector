from behaviour import Behaviour
import re
import time
from appium.webdriver.common.touch_action import TouchAction
from appium.webdriver.common.multi_action import MultiAction
from xml.etree import ElementTree as ET
import subprocess
from behaviour import clickActList,downSwipeActList,otherSwipeActList

class Operation:
    def __init__(self,tester):
        self.driver = tester.driver

        self.trueMainImg = tester.trueMainImg
        self.mainSimiLari = tester.mainSimiLari
        self.appName = tester.appName

        self.mainActiIma = tester.mainActiIma

        self.mainActiName = tester.mainActiName
        self.clarriWay = tester.clarriWay
        self.nowAct = tester.nowAct
        self.widt = tester.widt
        self.heit = tester.heit
        self.actRecord = tester.actRecord
        self.simiLari = tester.simiLari

        self.netCon = tester.netCon

        self.preRecFlow = 0
        self.preSubFlow = 0
        self.preProNum = 0
        self.preRom = 0

        self.timer = tester.timer

    def CheckAndInit(self):
        '''
        Checks the current state of the driver and initializes if necessary.

        The function:
        1. Checks the current view (either as an image or as XML) against a reference (trueMainImg).
        2. If not the same, it tries to reset the state by pressing keys or restarting the app.
        3. It will also attempt to handle errors or unanticipated states gracefully.

        :return: Boolean indicating whether initialization succeeded.
        '''
        
        def getCurrentView():
            '''Utility function to get the current view.'''
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

        # Step 1: Immediately compare without doing anything.
        nowPic = getCurrentView()
        if self.CheckIsSame(nowPic, self.trueMainImg, self.mainSimiLari):
            print('No action:', True)
            return True

        # Step 2: Simulate a back key press and check again.
        self.driver.press_keycode(4)
        time.sleep(0.5)

        nowPic = getCurrentView()
        if self.CheckIsSame(nowPic, self.trueMainImg, self.mainSimiLari):
            print('Exit action:', True)
            return True

        # Step 3: Try repeating the last action if there was one.
        if len(self.nowAct) > 0:
            behav = self.nowAct[-1]
            self.DoBehav(behav[0], behav[1], behav[-1])       
            time.sleep(0.5)
            nowPic = getCurrentView()
            if self.CheckIsSame(nowPic, self.trueMainImg, self.mainSimiLari):
                print('Action repeated:', True)
                return True

        # Step 4: Close the app.
        try:
            self.driver.terminate_app(self.appName)
        except:
            print('No need to terminate')

        # Step 5: Try to restart the app.
        try:
            self.driver.start_activity(self.appName, self.mainActiName)
        except:
            print('Error while starting! Retrying...')
            self.driver.press_keycode(4)
            time.sleep(0.1)
            self.driver.press_keycode(4)
            self.driver.start_activity(self.appName, self.mainActiName)

        isStart = self.WaitXml(12)
        if isStart:
            self.DoAct()

        nowPic = getCurrentView()
        print('Check trueMain:', self.compXml(self.mainActiIma, self.trueMainImg))

        if isStart and self.CheckIsSame(nowPic, self.trueMainImg, self.mainSimiLari):
            print('Reinitialized after restart')
            return True

        if not isStart:
            print('Waitxml error')
        else:
            print('Check same failed')

        print('Initialization failed!')
        return False
    def DoAct(self):
        '''Performs a series of actions defined in nowAct.'''
        for behav in self.nowAct:
            self.DoBehav(behav[0], behav[1], behav[-1])
            print('Action executed:', behav)

    def WaitXml(self, timeout=10):
        '''
        Waits until the current XML of the driver matches mainActiIma or until the timeout is reached.

        :param timeout: Time to wait in seconds.
        :return: Boolean indicating if the XML matched before the timeout.
        '''
        deadline = time.time() + timeout
        while time.time() < deadline:
            current_xml = self.driver.page_source
            if self.compXml(current_xml, self.mainActiIma, 0.05):
                return True
            time.sleep(.5)
        return False

    def CheckIsSame(self, firPic, secPic, simi):
        '''
        Compares two pictures or XMLs for similarity.

        :param firPic: First picture or XML.
        :param secPic: Second picture or XML.
        :param simi: Similarity threshold.
        :return: Boolean indicating if the two inputs are similar.
        '''
        if self.clarriWay == 'pic':
            return self.compareHist(firPic, secPic, simi)
        else:
            return self.compXml(firPic, secPic, simi)

    def GetTreeAllIds(self, rootNode, resultList):
        '''
        Recursively extracts all bounds attributes from an XML tree.

        :param rootNode: The current node in the XML tree.
        :param resultList: The list to store the bounds attributes.
        '''
        resId = rootNode.attrib.get('bounds')
        if resId and resId not in resultList:
            resultList.append(resId)

        for node in rootNode.getchildren():
            self.GetTreeAllIds(node, resultList)

    def compXml(self, firXml, secXml, simi=0.1):
        '''
        Compares two XML structures based on their bounds attributes.

        :param firXml: First XML string.
        :param secXml: Second XML string.
        :param simi: Similarity threshold.
        :return: Boolean indicating if the two XMLs are similar.
        '''
        if not firXml:
            return not secXml
        elif not secXml:
            return False

        firRoot, secRoot = ET.fromstring(firXml), ET.fromstring(secXml)
        firIdList, secIdList = [], []
        
        self.GetTreeAllIds(firRoot, firIdList)
        self.GetTreeAllIds(secRoot, secIdList)

        saNum, diNum = 0, 0

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
        
        return False if saNum == 0 else (diNum * 1.0 / saNum) < simi

    def GetRom(self):
        '''
        Fetches the free RAM available on the device.

        :return: Amount of free RAM.
        '''
        order = 'adb shell cat /proc/meminfo'
        pi = subprocess.Popen(order, shell=True, stdout=subprocess.PIPE)
        subRes = pi.stdout.read().decode('utf-8').replace("\n", " ").replace("\r", " ")
        free_ram = re.findall(r'MemFree:(.*?)MemAvailable:', subRes)[0].split()[0]
        return free_ram

    def GetProcNum(self):
        '''Fetches the number of processes related to appName.
        
        :return: Count of appName occurrences in the process list.
        '''
        order = 'adb shell ps | findstr ' + self.appName
        pi = subprocess.Popen(order, shell=True, stdout=subprocess.PIPE)
        subRes = pi.stdout.read().decode('utf-8')
        return subRes.count(self.appName)

    def GetAllNetflow(self):
        '''Fetches network flow data for the current connection method.
        
        :return: Tuple containing received bytes and sent bytes.
        '''
        order = 'adb shell cat /proc/net/dev'
        pi = subprocess.Popen(order, shell=True, stdout=subprocess.PIPE)
        subRes = pi.stdout.read().decode('utf-8').replace("\n", " ").replace("\r", " ")

        if self.netCon == 'wlan':
            pattern = r'wlan0:(.*?)[A-Za-z]'
        elif self.netCon == 'data':
            pattern = r' rmnet_data2:(.*?)[A-Za-z]'
        elif self.netCon == 'imitator':
            pattern = r' lo:(.*?) [A-Za-z]'

        net_data = re.findall(pattern, subRes)[0].split()
        recByte, subByte = net_data[0], net_data[8]
        return recByte, subByte

    def GetAllStatus(self):
        '''Fetches a variety of device status data, including netflow, process count, and available RAM.
        
        :return: Tuple containing the change in received bytes, sent bytes, process count, and available RAM.
        '''
        RecFlow, SubFlow = self.GetAllNetflow()
        ProNum = self.GetProcNum()
        Rom = self.GetRom()

        oneRec = int(RecFlow) - int(self.preRecFlow)
        oneSub = int(SubFlow) - int(self.preSubFlow)
        oneProNum = int(ProNum) - int(self.preProNum)
        oneRom = int(Rom) - int(self.preRom)

        self.preRecFlow = RecFlow
        self.preSubFlow = SubFlow
        self.preProNum = ProNum
        self.preRom = Rom

        return oneRec, oneSub, oneProNum, oneRom

    def TestOneBoundAllPagesCompareActList(self, bound, behavList, isSame=True):
        '''Compares the behavior list for a given bound.
        
        :param bound: Boundary to be tested.
        :param behavList: List of behaviors to be checked.
        :param isSame: Flag indicating whether to check for similarity.
        :return: List of operations that resulted in misbehaviors.
        '''
        misOpe = []
        
        # Initialize timer and check state.
        self.timer.navStart()
        self.CheckAndInit()
        self.timer.navOver()
        
        # Determine method to clarify (image or XML) and obtain the pre-action image or XML.
        preActImg = None
        try:
            preActImg = self.driver.screenshot() if self.clarriWay == 'pic' else self.driver.page_source
        except:
            pass
        
        # Extract numerical values from the bound and calculate middle coordinates.
        nums = re.findall(r"\d+", bound)
        lux, luy, rdx, rdy = map(int, nums)
        cliX, cliY = (lux + rdx) // 2, (luy + rdy) // 2
        
        # Ensure the coordinates are within screen boundaries.
        cliX = min(max(1, cliX), self.widt - 1)
        cliY = min(max(1, cliY), self.heit - 1)
        
        imgList = []
        statusList = []
        
        for behav in behavList:
            self.timer.genStart()
            
            # Initialize and start navigation timer.
            self.timer.navStart()
            self.CheckAndInit()
            self.timer.navOver()

            # Capture the status and perform the behavior.
            self.GetAllStatus()
            self.DoBehav(cliX, cliY, behav)
            self.timer.genOver()

            # Attempt to obtain the image or XML after the behavior.
            fir_cli_CenterImg = None
            try:
                fir_cli_CenterImg = self.driver.screenshot() if self.clarriWay == 'pic' else self.driver.page_source
            except:
                pass

            # Check similarity between images or XMLs.
            if not self.CheckIsSame(fir_cli_CenterImg, preActImg, self.simiLari):
                self.AddActiToList([cliX, cliY, behav])

                if any(self.CheckIsSame(fir_cli_CenterImg, cenImg, self.simiLari) for cenImg in imgList):
                    misOpe.append((cliX, cliY, behav))
                    self.timer.oraOver()
                    return misOpe

                imgList.append(fir_cli_CenterImg)
            else:
                oneRec, oneSub, oneProNum, oneRom = self.GetAllStatus()
                
                # If substantial deviations in system status are detected, log as misoperation.
                if any(abs(val) > threshold for val, threshold in zip([oneSub, oneRec, oneProNum, oneRom], [25000, 29000, 3, 3072])):
                    if imgList:
                        misOpe.append((cliX, cliY, behav))
                        self.timer.oraOver()
                        return misOpe

                theStatus = [oneRec, oneSub, oneProNum, oneRom]
                statusList.append(theStatus)

                # Calculate average deviations.
                AvgRec = sum(sta[0] - theStatus[0] for sta in statusList) / len(statusList)
                AvgSub = sum(sta[1] - theStatus[1] for sta in statusList) / len(statusList)
                AvgProNum = sum(sta[2] - theStatus[2] for sta in statusList) / len(statusList)
                AvgRom = sum(sta[3] - theStatus[3] for sta in statusList) / len(statusList)
                
                if any(abs(val) > threshold for val, threshold in zip([AvgRec, AvgSub, AvgProNum, AvgRom], [19000, 15000, 2, 2048])):
                    misOpe.append((cliX, cliY, behav))
                    self.timer.oraOver()
                    return misOpe
            
            self.timer.oraOver()

        return misOpe

    def TestOneBoundAllPagesCompareActListOld(self, bound, behavList, isSame=True):
        '''Tests behaviors within given boundary and compares images/pages for differences.
        
        :param bound: Boundary string containing coordinates.
        :param behavList: List of behaviors to be checked.
        :param isSame: Flag indicating the type of similarity check.
        :return: List of coordinates and behaviors that showed discrepancies.
        '''
        misOpe = []

        # Initialize the state.
        self.CheckAndInit()

        # Get the pre-action image or page source based on the clarification method.
        preActImg = None
        try:
            if self.clarriWay == 'pic':
                preActImg = self.driver.screenshot()
            else:
                preActImg = self.driver.page_source
        except:
            pass

        # Extract coordinates from the bound string and calculate the middle point.
        nums = re.findall(r"\d+", bound)
        lux, luy, rdx, rdy = map(int, nums)
        cliX, cliY = (lux + rdx) // 2, (luy + rdy) // 2

        # Ensure the coordinates lie within the screen boundaries.
        cliX = min(max(1, cliX), self.widt - 1)
        cliY = min(max(1, cliY), self.heit - 1)

        imgList = []
        for behav in behavList:
            # Re-initialize and execute the behavior.
            self.CheckAndInit()
            self.DoBehav(cliX, cliY, behav)

            # Get the image or page source after executing the behavior.
            fir_cli_CenterImg = None
            try:
                if self.clarriWay == 'pic':
                    fir_cli_CenterImg = self.driver.screenshot()
                else:
                    fir_cli_CenterImg = self.driver.page_source
            except:
                pass

            # Check the similarity with previous images/pages if the list isn't empty.
            if imgList:
                for cenImg in imgList:
                    if not self.CheckIsSame(fir_cli_CenterImg, preActImg, self.simiLari):
                        misOpe.append([cliX, cliY, behav])
                        self.AddActiToList([cliX, cliY, behav])

                        # Depending on the isSame flag, determine which similarity check to use.
                        checkCondition = not self.CheckIsSame(fir_cli_CenterImg, cenImg, self.simiLari) if isSame else self.CheckIsSame(fir_cli_CenterImg, cenImg, self.simiLari)
                        if checkCondition:
                            misOpe.append((cliX, cliY, behav))
                            break

            imgList.append(fir_cli_CenterImg)

        return misOpe

    def AddActiToList(self, act):
        '''Add activity to the list based on the action provided.

        :param act: Action to be recorded with the activity.
        '''
        try:
            # Retrieve page source from the driver.
            acti = self.driver.page_source  # Type: string
            
            # Command to get connected devices' information.
            order = 'adb shell dumpsys window | findstr mCurrentFocus'

            # Execute the command.
            pi = subprocess.Popen(order, shell=True, stdout=subprocess.PIPE)
            subRes = pi.stdout.read().decode('utf-8').replace("\n", " ").replace("\r", " ")

            # Check if the application is in focus.
            if self.appName not in subRes:
                print('Not this app')
                return
            # Retrieve current activity and associated actions.
        except:
            return

        # Add the retrieved activity and action to the record.
        self.actRecord.Add(acti, act)

    def DoBehav(self,cliX,cliY,behav):
        if behav == Behaviour.click:
            self.driver.tap([(cliX, cliY)])
        elif behav == Behaviour.tripleSwipe:
            self.TripFinCap(cliX,cliY,True)
        elif behav == Behaviour.doubleSwipe:
            self.TripFinCap(cliX,cliY,False)
        elif behav == Behaviour.doubleClick:
            print('doublecli')
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

    def TripFinCap(self, cliX, cliY, isTrip):
        '''Perform a multi-touch action on given coordinates.

        :param cliX: Initial X coordinate
        :param cliY: Initial Y coordinate
        :param isTrip: Boolean flag to determine if the third touch action is needed
        '''
        
        # Ensure cliX and cliY are within the screen bounds
        cliX = max(1, min(cliX, self.widt - 1))
        cliY = max(1, min(cliY, self.heit - 1))
        
        diX = cliX
        diY = cliY + 200
        leX = max(1, diX - 30)
        riX = min(self.widt - 1, diX + 30)
        diY = min(self.heit - 1, diY)

        # Define touch actions for given coordinates
        action1 = TouchAction(self.driver)
        action1.press(x=leX, y=cliY).wait(300).move_to(x=leX, y=diY).wait(300).release()
        
        action2 = TouchAction(self.driver)
        action2.press(x=cliX, y=cliY).wait(300).move_to(x=diX, y=diY).wait(300).release()

        # Create a multi-touch action object
        multi_action = MultiAction(self.driver)
        multi_action.add(action1, action2)

        # Add a third touch action if isTrip is True
        if isTrip:
            action3 = TouchAction(self.driver)        
            action3.press(x=riX, y=cliY).wait(300).move_to(x=riX, y=diY).wait(300).release()
            multi_action.add(action3)

        # Execute the multi-touch actions
        try:
            multi_action.perform()
        except:
            print('Screenshot forbidden!')

        # Perform swipe action on the driver
        self.driver.swipe(cliX, cliY, diX, diY)
