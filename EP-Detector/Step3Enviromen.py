from behaviour import Behaviour
import re
import time
from appium.webdriver.common.touch_action import TouchAction
from appium.webdriver.common.multi_action import MultiAction
import subprocess
from xml.etree import ElementTree as ET
from behaviour import clickActList,downSwipeActList,otherSwipeActList

class Enviromen:
    def __init__(self,tester):
        self.driver = tester.driver
        self.netCon = tester.netCon
        self.trueMainImg = tester.trueMainImg
        self.mainSimiLari =  0.9 # tester.mainSimiLari
        self.appName = tester.appName

        self.mainActiIma = tester.mainActiIma

        self.mainActiName = tester.mainActiName
        self.clarriWay = tester.clarriWay
        self.nowAct = tester.nowAct
        self.widt = tester.widt
        self.heit = tester.heit
        self.actRecord = tester.actRecord
        self.simiLari = tester.simiLari

        self.preRecFlow = 0
        self.preSubFlow = 0
        self.preProNum = 0
        self.preRom = 0

        self.timer = tester.timer
        self.WeakenEnv()

    def WeakenEnv(self):
        '''Set the CPU governor mode to 'powersave' using adb command.'''
        order = 'adb shell echo powersave > /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor'
        subprocess.Popen(order, shell=True, stdout=subprocess.PIPE)

    def CheckAndInit(self):
        '''Check and initialize the app to a specific state based on visual or page source comparison.

        The method tries to compare the current state of the app to a predefined "true" state.
        It employs various actions (like keypresses) and checks to ensure the app reaches this state.
        '''

        def get_current_state():
            '''Get the current state of the app either as a screenshot or page source.'''
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

        # Check if current state matches without any action
        nowPic = get_current_state()
        theres = self.CheckIsSame(nowPic, self.trueMainImg, self.mainSimiLari)
        print('No action:', theres)
        if theres:
            return True

        # Perform back key action and then check state again
        self.driver.press_keycode(4)
        time.sleep(0.5)
        nowPic = get_current_state()
        theres = self.CheckIsSame(nowPic, self.trueMainImg, self.mainSimiLari)
        print('Exit action:', theres)
        if theres:
            return True

        # Check if any previous actions were stored and execute them
        if len(self.nowAct) > 0:
            behav = self.nowAct[-1]
            self.DoBehav(behav[0], behav[1], behav[-1])       
            time.sleep(0.5)
            nowPic = get_current_state()
            if self.CheckIsSame(nowPic, self.trueMainImg, self.mainSimiLari):
                return True

        # If still not matched, try to restart the app
        try:
            self.driver.terminate_app(self.appName)  # Close app
        except:
            print('No need to terminate app')

        # Try to relaunch the app activity
        try:
            self.driver.start_activity(self.appName, self.mainActiName)
        except:
            print('Error while starting activity!')
            self.driver.press_keycode(4)
            time.sleep(0.1)
            self.driver.press_keycode(4)
            self.driver.start_activity(self.appName, self.mainActiName)

        isStart = self.WaitXml(12)
        if isStart:
            self.DoAct()

        nowPic = get_current_state()
        print('checktrueMain', self.compXml(self.mainActiIma, self.trueMainImg))

        if isStart and self.CheckIsSame(nowPic, self.trueMainImg, self.mainSimiLari):
            return True
        elif not isStart:
            print('waitxml error')
        else:
            print('Check same failed')

        print('Initialization failed!')
        return False

    def DoAct(self):
        '''Execute a sequence of behaviors/actions from the "nowAct" list.'''
        for behav in self.nowAct:
            self.DoBehav(behav[0], behav[1], behav[-1])
            print('Behavior:', behav)

    def compXml(self, firXml, secXml, simi=0.1):
        '''Compare two XML strings based on similarity measure.

        Args:
            firXml (str): First XML string.
            secXml (str): Second XML string.
            simi (float): Similarity threshold.

        Returns:
            bool: True if the XMLs are similar within the threshold, otherwise False.
        '''
        
        if firXml is None:
            return secXml is None
        elif secXml is None:
            return False

        firRoot = ET.fromstring(firXml)
        secRoot = ET.fromstring(secXml)

        firIdList = []
        secIdList = []
        
        # Get all IDs from both XML trees
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
        
        if saNum == 0:
            return False

        print('Difference Ratio:', diNum, saNum)
        return (diNum*1.0/saNum) < simi

    def GetTreeAllIds(self, rootNode, resultList):
        '''Recursively extract all unique IDs from an XML tree.

        Args:
            rootNode (ET.Element): The starting XML tree node.
            resultList (list): List to store extracted IDs.
        '''
        
        resId = rootNode.attrib.get('bounds')

        if resId and resId not in resultList:
            resultList.append(resId)

        for node in rootNode.getchildren():
            self.GetTreeAllIds(node, resultList)

    def WaitXml(self, timeout=10):
        '''Wait for a specific XML state within a timeout.

        Args:
            timeout (int): Duration in seconds to wait for the desired XML state.

        Returns:
            bool: True if desired XML state is found, otherwise False.
        '''
        
        deadline = time.time() + timeout
        while time.time() < deadline:
            current_xml = self.driver.page_source
            if self.compXml(current_xml, self.mainActiIma, 0.05):
                return True
            time.sleep(0.5)
        return False

    def CheckIsSame(self, firPic, secPic, simi):
        '''Check if two given inputs (either images or XMLs) are similar.

        Args:
            firPic (str): First input (either image path or XML string).
            secPic (str): Second input (either image path or XML string).
            simi (float): Similarity threshold.

        Returns:
            bool: True if inputs are similar within the threshold, otherwise False.
        '''
        
        if self.clarriWay == 'pic':
            return self.compareHist(firPic, secPic, simi)
        else:
            return self.compXml(firPic, secPic, simi)

    def TestOneBoundAllPagesInEnvironment(self, bound):
        '''Tests a boundary over all pages in the current environment.
        
        Args:
            bound (str): A string representing the boundary coordinates.
            
        Returns:
            list: List of misoperations detected during the test.
        '''
        
        misOpe = []
        self.timer.navStart()
        self.CheckAndInit()
        self.timer.navOver()
        self.timer.genStart()

        # Fetching the image or page source based on the "clarriWay"
        preActImg = self.driver.screenshot() if self.clarriWay == 'pic' else self.driver.page_source

        # Extracting coordinates from the boundary string
        nums = re.findall(r"\d+", bound)
        lux, luy, rdx, rdy = map(int, nums)
        
        # Calculating the middle of the coordinates
        midX, midY = (lux+rdx) // 2, (luy+rdy) // 2

        # Ensuring the coordinates are within valid range
        cliX, cliY = min(max(1, midX), self.widt-1), min(max(1, midY), self.heit-1)

        # Perform click action at the calculated coordinate
        self.DoBehav(cliX, cliY, Behaviour.click)
        time.sleep(1)
        self.timer.genOver()

        # Fetching the image or page source post action
        fir_cli_CenterImg = self.driver.screenshot() if self.clarriWay == 'pic' else self.driver.page_source

        self.GetAllStatus()
        mybehav = Behaviour.doubleClick

        # Decide behavior based on similarity check
        if self.CheckIsSame(fir_cli_CenterImg, preActImg, self.simiLari):
            self.timer.genStart()
            self.DoBehav(cliX, cliY, Behaviour.doubleClick)
            self.timer.genOver()
            mybehav = Behaviour.doubleClick
        else:
            self.AddActiToList([cliX, cliY, Behaviour.click])
            self.timer.genStart()
            self.DoBehav(cliX, cliY, Behaviour.click)
            self.timer.genOver()

        self.timer.oraStart()

        # Extract all status metrics
        oneRec, oneSub, oneProNum, oneRom = self.GetAllStatus()
        print('oneNet:', oneRec, oneSub)
        print('Pro  Rom:', oneProNum, oneRom)

        r, g, b = 50, 50, 50
        # Check for anomalies in the extracted metrics and adjust RGB values
        if abs(oneSub) > 25000 or abs(oneRec) > 29000 or abs(oneProNum) > 3 or abs(oneRom) > 10240:
            r = 190 if abs(oneSub) > 15000 or abs(oneRec) > 19000 else r
            g = 190 if abs(oneProNum) > 2 else g
            b = 190 if abs(oneRom) > 1536 else b
            misOpe.append((cliX, cliY, (r, g, b), mybehav.value))

        self.timer.oraOver()

        return misOpe

    def AddActiToList(self, act):
        '''Adds the action to the activity record.
        
        Args:
            act: The action to be recorded.
        '''
        try:
            acti = self.driver.page_source  # of type string
            order = 'adb shell dumpsys window | findstr mCurrentFocus'  # Retrieve connected device

            pi = subprocess.Popen(order, shell=True, stdout=subprocess.PIPE)
            subRes = pi.stdout.read().decode('utf-8').replace("\n", " ").replace("\r", " ")

            # Check if the current activity belongs to the target app
            if self.appName not in subRes:
                print('Not this app')
                return

        except:
            return

        print('Added to list!')
        self.actRecord.Add(acti, act)


    def GetAllStatus(self):
        '''Fetch all status metrics and calculate the difference from previous values.'''
        
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


    def GetNetflow(self):
        '''Retrieve network flow information for the application.'''
        
        order = 'adb shell pidof ' + self.appName
        pi = subprocess.Popen(order, shell=True, stdout=subprocess.PIPE)
        pid = pi.stdout.read().decode('utf-8').replace("\n", " ").replace("\r", " ")

        order = 'adb shell cat /proc/' + pid + '/net/dev'
        pi = subprocess.Popen(order, shell=True, stdout=subprocess.PIPE)
        subRes = pi.stdout.read().decode('utf-8').replace("\n", " ").replace("\r", " ")

        re1 = r'wlan0:(.*?)rmnet_data2'
        values = re.findall(re1, subRes)[0].split()
        recByte, subByte = values[0], values[8]

        return recByte, subByte


    def GetRom(self):
        '''Retrieve the free memory information.'''
        
        order = 'adb shell cat /proc/meminfo'
        pi = subprocess.Popen(order, shell=True, stdout=subprocess.PIPE)
        subRes = pi.stdout.read().decode('utf-8').replace("\n", " ").replace("\r", " ")

        re1 = r'MemFree:(.*?)MemAvailable:'
        freeMemory = re.findall(re1, subRes)[0].split()[0]

        return freeMemory


    def GetCpuInfo(self):
        '''Retrieve the CPU usage information for the application.'''
        
        order = 'adb shell "dumpsys cpuinfo | grep ' + self.appName + '"'
        pi = subprocess.Popen(order, shell=True, stdout=subprocess.PIPE)
        res = pi.stdout.read().decode('utf-8')

        cpuUsage = res.split("%")[0]

        return cpuUsage

    def GetProcNum(self):
        '''Get the number of processes for the application.'''
        
        order = 'adb shell ps | findstr ' + self.appName
        pi = subprocess.Popen(order, shell=True, stdout=subprocess.PIPE)
        subRes = pi.stdout.read().decode('utf-8')

        return subRes.count(self.appName)

    def GetAllNetflow(self):
        '''Fetch network flow information based on the network connection type.
        
        Returns:
            tuple: Received and submitted bytes.
        '''
        order = 'adb shell cat /proc/net/dev'  # Retrieve connected device
        pi = subprocess.Popen(order, shell=True, stdout=subprocess.PIPE)
        subRes = pi.stdout.read().decode('utf-8').replace("\n", " ").replace("\r", " ")

        # Determine the pattern to search based on the network connection type
        if self.netCon == 'wlan':
            re1 = r'wlan0:(.*?)[A-Za-z]'
        elif self.netCon == 'data':
            re1 = r' rmnet_data2:(.*?)[A-Za-z]'
        elif self.netCon == 'imitator':
            re1 = r' lo:(.*?) [A-Za-z]'

        network_values = re.findall(re1, subRes)[0].split()
        recByte = network_values[0]
        subByte = network_values[8]

        return recByte, subByte

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
        '''
        Adjusts the x and y coordinates within the screen boundaries and 
        creates a multi-touch action sequence that possibly involves up to three touch points.
        
        Args:
        cliX (int): Initial x-coordinate.
        cliY (int): Initial y-coordinate.
        isTrip (bool): If True, a third touch point is involved in the sequence.
        '''
        
        # Adjust the coordinates within the screen boundaries
        cliX = max(1, min(cliX, self.widt - 1))
        cliY = max(1, min(cliY, self.heit - 1))
        
        diX = cliX
        diY = cliY + 200
        diY = min(diY, self.heit - 1)
        
        leX = max(1, diX - 30)
        riX = min(self.widt - 1, diX + 30)
        
        # Define touch actions
        action1 = TouchAction(self.driver)
        action1.press(x=leX, y=cliY).wait(300).move_to(x=leX, y=diY).wait(300).release()
        
        action2 = TouchAction(self.driver)
        action2.press(x=cliX, y=cliY).wait(300).move_to(x=diX, y=diY).wait(300).release()

        # Create multi-touch action object
        multi_action = MultiAction(self.driver)
        multi_action.add(action1, action2)
        
        # If trip action is needed, add a third action
        if isTrip:
            action3 = TouchAction(self.driver)
            action3.press(x=riX, y=cliY).wait(300).move_to(x=riX, y=diY).wait(300).release()
            multi_action.add(action3)
        
        # Execute the multi-touch action sequence
        multi_action.perform()

        # Execute the swipe action
        self.driver.swipe(cliX, cliY, diX, diY)



