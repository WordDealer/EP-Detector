from behaviour import Behaviour
import re
import time
from appium.webdriver.common.touch_action import TouchAction
from appium.webdriver.common.multi_action import MultiAction
from xml.etree import ElementTree as ET
from behaviour import Behaviour
import re
import time
from appium.webdriver.common.touch_action import TouchAction
from appium.webdriver.common.multi_action import MultiAction
from xml.etree import ElementTree as ET
import subprocess
from behaviour import clickActList, downSwipeActList, otherSwipeActList

class Spacing:
    def __init__(self, tester):
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
        self.misTouch = tester.misTouch
        self.preRecFlow = 0
        self.preSubFlow = 0
        self.preProNum = 0
        self.preRom = 0
        self.timer = tester.timer

    def CheckAndInit(self):
        '''
        This function checks and initializes the application's state. The primary purpose is to
        confirm the application's state by either comparing screenshots or the page source, and then 
        take appropriate actions based on the comparison results.
        '''

        # Step 1: Immediate comparison without any action
        nowPic = self._capture_screenshot_or_page_source()

        is_same = self.CheckIsSame(nowPic, self.trueMainImg, self.mainSimiLari)
        print('No action:', is_same)
        if is_same:
            return True

        # Simulate a back press and wait for half a second
        self.driver.press_keycode(4)
        time.sleep(0.5)

        nowPic = self._capture_screenshot_or_page_source()
        is_same_after_back = self.CheckIsSame(nowPic, self.trueMainImg, self.mainSimiLari)
        print('Exit action:', is_same_after_back)
        if is_same_after_back:
            return True

        # Check if the current state matches the expected state after pressing back
        if is_same_after_back:
            return True

        # If we have recorded actions, revert the last action
        if len(self.nowAct) > 0:
            behav = self.nowAct[-1]
            self.DoBehav(behav[0], behav[1], behav[-1])
            time.sleep(0.5)
            
            nowPic = self._capture_screenshot_or_page_source()

            if self.CheckIsSame(nowPic, self.trueMainImg, self.mainSimiLari):
                return True

        # If state mismatch or unable to skip ads, restart the app
        self._restart_app()

        nowPic = self._capture_screenshot_or_page_source()

        print('Check trueMain:', self.compXml(self.mainActiIma, self.trueMainImg))

        is_started = self.WaitXml(12)
        if is_started and self.CheckIsSame(nowPic, self.trueMainImg, self.mainSimiLari):
            return True

        if not is_started:
            print('WaitXml error')
        else:
            print('Check same failed')

        print('Initialization failed!')
        return False

    def _capture_screenshot_or_page_source(self):
        '''
        Helper function to capture either a screenshot or the page source based on the clarification method.
        '''
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

    def _restart_app(self):
        '''
        Helper function to terminate and restart the application.
        '''
        try:
            self.driver.terminate_app(self.appName)
        except:
            print('No need to terminate')

        try:
            self.driver.start_activity(self.appName, self.mainActiName)
        except:
            print('Error!!')
            self.driver.press_keycode(4)
            time.sleep(0.1)
            self.driver.press_keycode(4)
            self.driver.start_activity(self.appName, self.mainActiName)

    def DoAct(self):
        '''
        Execute actions based on the current list of behaviors.
        '''
        for behav in self.nowAct:
            self.DoBehav(behav[0], behav[1], behav[-1])
            print('beh', behav)

    def WaitXml(self, timeout=10):
        '''
        Wait until the current page's XML matches the main activity's XML or the timeout is reached.
        :param timeout: Maximum time to wait in seconds
        :return: True if XML matches before timeout, else False
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
        Check if the first picture/source and the second picture/source are similar.
        :param firPic: First picture or XML
        :param secPic: Second picture or XML
        :param simi: Similarity threshold
        :return: True if similar, else False
        '''
        if self.clarriWay == 'pic':
            return self.compareHist(firPic, secPic, simi)
        else:
            return self.compXml(firPic, secPic, simi)

    def GetTreeAllIds(self, rootNode, resultList):
        '''
        Recursively gather all IDs from the XML tree starting from the rootNode.
        :param rootNode: Starting node for the search
        :param resultList: List to store the found IDs
        '''
        resId = rootNode.attrib.get('bounds')  # resource-id
        if resId and resId not in resultList:
            resultList.append(resId)
        for node in rootNode.getchildren():
            self.GetTreeAllIds(node, resultList)

    def compXml(self, firXml, secXml, simi=0.1):
        '''
        Compare two XML structures based on their IDs and determine if they are similar.
        :param firXml: First XML string
        :param secXml: Second XML string
        :param simi: Similarity threshold
        :return: True if similar, else False
        '''
        if firXml is None:
            return secXml is None
        elif secXml is None:
            return False

        firRoot = ET.fromstring(firXml)
        secRoot = ET.fromstring(secXml)

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
            if secId not in firIdList:
                diNum += 1

        if saNum == 0:
            return False

        return (diNum * 1.0 / saNum) < simi
    def GetTreeAllSpa(self, rootNode, resultList):
        '''
        Recursively gather all bounds, clickable, and scrollable attributes from the XML tree starting from the rootNode.
        :param rootNode: Starting node for the search
        :param resultList: List to store the found attributes
        '''
        bounds = rootNode.attrib.get('bounds')
        cliAble = rootNode.attrib.get('clickable')  # Get clickable attribute
        scroAble = rootNode.attrib.get('scrollable')  # Get scrollable attribute

        if (cliAble == "true" or scroAble == "true") and bounds and (bounds not in resultList):
            resultList.append((bounds, cliAble, scroAble))

        for node in rootNode.getchildren():
            self.GetTreeAllSpa(node, resultList)

    def ScanPage(self, cliResultList, scrResultList):
        '''
        Scan the page for clickable and scrollable areas, determine if they are mis-clicked, and return their coordinates.
        :param cliResultList: List of clickable areas
        :param scrResultList: List of scrollable areas
        :return: List of mis-clicked coordinates
        '''
        misOpe = []

        # Check clickable areas for mis-clicks
        for bound in cliResultList:
            self.timer.conStart()

            nums = re.findall(r"\d+", bound)
            lux, luy, rdx, rdy = [int(n) for n in nums]

            width, height = rdx - lux, rdy - luy
            print('width, height', width, height)

            if width < self.misTouch or height < self.misTouch:
                midX, midY = int((lux + rdx) * 0.5), int((luy + rdy) * 0.5)
                if self.CheckSpacingError(midX, midY, Behaviour.click):
                    misOpe.append([midX, midY])

            self.timer.conOver()

        # Check scrollable areas for mis-clicks
        for bound in scrResultList:
            self.timer.conStart()

            nums = re.findall(r"\d+", bound)
            lux, luy, rdx, rdy = [int(n) for n in nums]

            width, height = rdx - lux, rdy - luy
            print('width, height', width, height)

            if width < self.misTouch or height < self.misTouch:
                midX, midY = int((lux + rdx) * 0.5), int((luy + rdy) * 0.5)
                if self.CheckSpacingError(midX, midY, Behaviour.downSwipe):
                    misOpe.append([midX, midY])

            self.timer.conOver()

        return misOpe

    def GetRom(self):
        '''
        Retrieve the available memory from the device.
        :return: Available memory in string format.
        '''
        order = 'adb shell cat /proc/meminfo'
        pi = subprocess.Popen(order, shell=True, stdout=subprocess.PIPE)
        subRes = pi.stdout.read().decode('utf-8').replace("\n", " ").replace("\r", " ")
        memFreePattern = r'MemFree:(.*?)MemAvailable:'
        freeMem = re.findall(memFreePattern, subRes)[0].split()[0]
        return freeMem

    def GetProcNum(self):
        '''
        Get the number of processes related to the specified app name.
        :return: Number of processes for the app.
        '''
        order = 'adb shell ps | findstr ' + self.appName
        pi = subprocess.Popen(order, shell=True, stdout=subprocess.PIPE)
        subRes = pi.stdout.read().decode('utf-8')
        return subRes.count(self.appName)

    def GetAllNetflow(self):
        '''
        Retrieve network flow information based on the connection type.
        :return: Received and submitted bytes in tuple format.
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
        netDetails = re.findall(pattern, subRes)[0].split()
        recByte, subByte = netDetails[0], netDetails[8]
        return recByte, subByte

    def GetAllStatus(self):
        '''
        Get the current status of network flow, processes, and memory.
        :return: Differences in received bytes, submitted bytes, process count, and memory from the previous state.
        '''
        RecFlow, SubFlow = self.GetAllNetflow()
        ProNum = self.GetProcNum()
        Rom = self.GetRom()

        oneRec = int(RecFlow) - int(self.preRecFlow)
        oneSub = int(SubFlow) - int(self.preSubFlow)
        oneProNum = int(ProNum) - int(self.preProNum)
        oneRom = int(Rom) - int(self.preRom)

        self.preRecFlow, self.preSubFlow, self.preProNum, self.preRom = RecFlow, SubFlow, ProNum, Rom

        return oneRec, oneSub, oneProNum, oneRom

    def CheckSpacingError(self, midX, midY, behv):
        '''
        Check for spacing errors by simulating behavior and comparing the results.
        :param midX: X coordinate.
        :param midY: Y coordinate.
        :param behv: Specified behavior like clicking or swiping.
        :return: Boolean indicating the presence of spacing error.
        '''
        self.timer.genStart()
        self.timer.navStart()
        self.CheckAndInit()
        self.timer.navOver()
        self.GetAllStatus()
        self.DoBehav(midX, midY, behv)

        # Get pre-action image or page source based on the clarriWay attribute.
        preActImg = self.driver.screenshot() if self.clarriWay == 'pic' else self.driver.page_source

        self.timer.genOver()
        PreOneRec, PreOneSub, PreOneProNum, PreOneRom = self.GetAllStatus()

        for beh in [[midX, midY], [midX, midY]]:
            self.timer.genStart()
            self.timer.navStart()
            self.CheckAndInit()
            self.timer.navOver()
            self.GetAllStatus()
            self.DoBehav(beh[0], beh[1], behv)
            self.timer.genOver()

            # Get post-action image or page source based on the clarriWay attribute.
            fir_cli_CenterImg = self.driver.screenshot() if self.clarriWay == 'pic' else self.driver.page_source

            # Compare the pre-action and post-action states to check for errors.
            if not self.CheckIsSame(fir_cli_CenterImg, preActImg, self.simiLari):
                self.AddActiToList([midX, midY, behv])
                self.timer.oraOver()
                return True

            oneRec, oneSub, oneProNum, oneRom = self.GetAllStatus()

            # Check for significant changes in metrics to detect errors.
            if any([abs(val) > threshold for val, threshold in zip([oneRec, oneSub, oneProNum, oneRom], [9000, 5000, 1, 512])]):
                self.timer.oraOver()
                return True

            self.timer.oraOver()

        return False

    def AddActiToList(self, act):
        '''
        Add an activity to the activity record list if it's related to the target app.
        :param act: Activity to be added to the list.
        '''
        try:
            # Obtain page source from the driver.
            acti = self.driver.page_source  # of type string

            # Command to get current focus information.
            order = 'adb shell dumpsys window | findstr mCurrentFocus'
            pi = subprocess.Popen(order, shell=True, stdout=subprocess.PIPE)
            subRes = pi.stdout.read().decode('utf-8').replace("\n", " ").replace("\r", " ")

            # Ensure the app is in focus.
            if self.appName not in subRes:
                print('Not the target app.')
                return

        except:
            return

        # Add the obtained activity and the action to the activity record.
        self.actRecord.Add(acti, act)

    def DoBehav(self, cliX, cliY, behav):
        if behav == Behaviour.click:
            self.driver.tap([(cliX, cliY)])
        elif behav == Behaviour.tripleSwipe:
            self.TripFinCap(cliX, cliY, True)
        elif behav == Behaviour.doubleSwipe:
            self.TripFinCap(cliX, cliY, False)
        elif behav == Behaviour.doubleClick:
            print('doublecli')
            self.driver.tap([(cliX, cliY)])
            time.sleep(0.1)
            self.driver.tap([(cliX, cliY)])
            time.sleep(1.5)
        elif behav == Behaviour.noneBehaviour:
            pass
        elif behav == Behaviour.misDoubleClick1:
            self.driver.tap([(cliX, cliY)])
            time.sleep(0.1)
            self.driver.tap([(cliX, cliY)], 300)
            time.sleep(1.5)
        elif behav == Behaviour.misDoubleClick2:
            self.driver.tap([(cliX, cliY)], 300)
            time.sleep(0.1)
            self.driver.tap([(cliX, cliY)])
            time.sleep(1.5)

        elif behav == Behaviour.longClick:
            self.driver.tap([(cliX, cliY)], 800)

        elif behav == Behaviour.leftSwipe:
            self.DoSwipe(cliX, cliY, "left", "swip")
        elif behav == Behaviour.rightSwipe:
            self.DoSwipe(cliX, cliY, "right", "swip")
        elif behav == Behaviour.upSwipe:
            self.DoSwipe(cliX, cliY, "up", "swip")
        elif behav == Behaviour.downSwipe:
            self.DoSwipe(cliX, cliY, "down", "swipe")

        elif behav == Behaviour.leftScroll:
            self.DoSwipe(cliX, cliY, "left", "scroll")
        elif behav == Behaviour.rightScroll:
            self.DoSwipe(cliX, cliY, "right", "scroll")
        elif behav == Behaviour.upScroll:
            self.DoSwipe(cliX, cliY, "up", "scroll")
        elif behav == Behaviour.downScroll:
            self.DoSwipe(cliX, cliY, "down", "scroll")

        elif behav == Behaviour.misLongClick1:
            self.driver.tap([(cliX, cliY)])
            time.sleep(0.1)
            self.driver.tap([(cliX, cliY)], 800)


        elif behav == Behaviour.misLongClick2:
            self.driver.tap([(cliX, cliY)], 200)

        elif behav == Behaviour.misLeftSwipe:
            self.driver.tap([(cliX, cliY)])
            time.sleep(0.1)
            self.DoSwipe(cliX, cliY, "left", "swip")
        elif behav == Behaviour.misRightSwipe:
            self.driver.tap([(cliX, cliY)])
            time.sleep(0.1)
            self.DoSwipe(cliX, cliY, "right", "swip")
        elif behav == Behaviour.misUpSwipe:
            self.driver.tap([(cliX, cliY)])
            time.sleep(0.1)
            self.DoSwipe(cliX, cliY, "up", "swip")
        elif behav == Behaviour.misDownSwipe:
            self.driver.tap([(cliX, cliY)])
            time.sleep(0.1)
            self.DoSwipe(cliX, cliY, "down", "swipe")
        elif behav == Behaviour.misLeftScroll1:
            self.driver.tap([(cliX, cliY)])
            time.sleep(0.1)
            self.DoSwipe(cliX, cliY, "left", "scroll")
        elif behav == Behaviour.misRightScroll1:
            self.driver.tap([(cliX, cliY)])
            time.sleep(0.1)
            self.DoSwipe(cliX, cliY, "right", "scroll")
        elif behav == Behaviour.misUpScroll1:
            self.driver.tap([(cliX, cliY)])
            time.sleep(0.1)
            self.DoSwipe(cliX, cliY, "up", "scroll")
        elif behav == Behaviour.misDownScroll1:
            self.driver.tap([(cliX, cliY)])
            time.sleep(0.1)
            self.DoSwipe(cliX, cliY, "down", "scroll")

        elif behav == Behaviour.misLeftScroll2:
            self.DoMisScroll2(cliX, cliY, "left", "scroll")
        elif behav == Behaviour.misRightScroll2:
            self.DoMisScroll2(cliX, cliY, "right", "scroll")
        elif behav == Behaviour.misUpScroll2:
            self.DoMisScroll2(cliX, cliY, "up", "scroll")
        elif behav == Behaviour.misDownScroll2:
            self.DoMisScroll2(cliX, cliY, "down", "scroll")
        elif behav == Behaviour.misLeftScroll3:
            self.DoMisScroll3(cliX, cliY, "left", 3)
        elif behav == Behaviour.misRightScroll3:
            self.DoMisScroll3(cliX, cliY, "right", 3)
        elif behav == Behaviour.misUpScroll3:
            self.DoMisScroll3(cliX, cliY, "up", 3)
        elif behav == Behaviour.misDownScroll3:
            self.DoMisScroll3(cliX, cliY, "down", 3)

        elif behav == Behaviour.misLeftScroll4:
            self.DoMisScroll3(cliX, cliY, "left", 4)
        elif behav == Behaviour.misRightScroll4:
            self.DoMisScroll3(cliX, cliY, "right", 4)
        elif behav == Behaviour.misUpScroll4:
            self.DoMisScroll3(cliX, cliY, "up", 4)
        elif behav == Behaviour.misDownScroll4:
            self.DoMisScroll3(cliX, cliY, "down", 4)

        elif behav == Behaviour.misLeftScroll5:
            self.DoMisScroll3(cliX, cliY, "left", 5)
        elif behav == Behaviour.misRightScroll5:
            self.DoMisScroll3(cliX, cliY, "right", 5)
        elif behav == Behaviour.misUpScroll5:
            self.DoMisScroll3(cliX, cliY, "up", 5)
        elif behav == Behaviour.misDownScroll5:
            self.DoMisScroll3(cliX, cliY, "down", 5)

    def DoMisScroll2(self, cliX, cliY, dir, actype):
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
        if actype == "swipe":
            self.driver.swipe(cliX, cliY, diX, diY)
        else:
            self.driver.swipeAndHold(cliX, cliY, diX, diY, 200)

        time.sleep(0.1)
        self.driver.tap([(diX, diY)], 500)

    def DoMisScroll3(self, cliX, cliY, dir, actype, misType):
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

        midX = int((diX + diX) * 0.5)
        midY = int((diY + diY) * 0.5)

        if misType == 3:
            self.driver.swipeAndHold(cliX, cliY, midX, midY, 100)
            self.driver.tap([(midX, midY)], 500)
            self.driver.swipeAndHold(midX, midY, diX, diY, 100)
        elif misType == 4:
            self.driver.swipe(cliX, cliY, midX, midY)
            time.sleep(0.1)
            self.driver.swipeAndHold(midX, midY, diX, diY, 100)
        else:
            self.driver.swipeAndHold(cliX, cliY, midX, midY, 100)
            time.sleep(0.1)
            self.driver.swipeAndHold(midX, midY, diX, diY, 100)

    def DoSwipe(self, cliX, cliY, dir, actype):

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
        if actype == "swipe":
            self.driver.swipe(cliX, cliY, diX, diY)
        else:
            self.driver.swipeAndHold(cliX, cliY, diX, diY, 200)

    def TripFinCap(self, cliX, cliY, isTrip):
        '''
        Performs touch actions on the screen based on the provided coordinates and conditions.
        :param cliX: X-coordinate for the touch action.
        :param cliY: Y-coordinate for the touch action.
        :param isTrip: A flag determining whether a third action is required.
        '''
        # Ensure coordinates are within the screen boundaries.
        cliX = max(1, min(cliX, self.widt - 1))
        cliY = max(1, min(cliY, self.heit - 1))

        diX = cliX
        diY = cliY

        # Calculate left and right boundaries for touch actions.
        leX = max(1, diX - 30)
        riX = min(self.widt - 1, diX + 30)
        diY = min(self.heit - 1, diY + 200)

        action1 = TouchAction(self.driver)
        action2 = TouchAction(self.driver)

        # Define the move actions for the touch.
        action1.press(x=leX, y=cliY).wait(300).move_to(x=leX, y=diY).wait(300).release()
        action2.press(x=cliX, y=cliY).wait(300).move_to(x=diX, y=diY).wait(300).release()

        # Create multi-touch action object.
        multi_action = MultiAction(self.driver)
        
        # Add action1 and action2 to the multi-touch action.
        multi_action.add(action1)
        multi_action.add(action2)

        # If isTrip flag is True, add a third touch action.
        if isTrip:
            action3 = TouchAction(self.driver)
            action3.press(x=riX, y=cliY).wait(300).move_to(x=riX, y=diY).wait(300).release()
            multi_action.add(action3)

        # Try executing the multi-touch action.
        try:
            multi_action.perform()
        except:
            print('Screenshot forbidden!!')
        
        # Swipe gesture.
        self.driver.swipe(cliX, cliY, diX, diY)




