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
        # #第一步什么都不做，立刻比较，确认是否一致

        if self.clarriWay == 'pic':
            try:
                nowPic = self.driver.screenshot()
            except:
                nowPic = None
        else:
            try:
                nowPic = self.driver.page_source
            except:
                nowPic = None

        theres = self.CheckIsSame(nowPic, self.trueMainImg, self.mainSimiLari)
        print('no act:', theres)
        if theres:
            return True

        self.driver.press_keycode(4)
        time.sleep(0.5)
        # #这里wait的是当前acti名字

        if self.clarriWay == 'pic':
            try:
                nowPic = self.driver.screenshot()
            except:
                nowPic = None
        else:
            try:
                nowPic = self.driver.page_source
            except:
                nowPic = None

        theres = self.CheckIsSame(nowPic, self.trueMainImg, self.mainSimiLari)
        print('exit act:', theres)
        if theres:
            return True

        if self.CheckIsSame(nowPic, self.trueMainImg, self.mainSimiLari):  # 如果开启了这个应用检查是否一样
            # print('返回键后回归初始化状态')
            return True

        if len(self.nowAct) > 0:
            behav = self.nowAct[-1]
            self.DoBehav(behav[0], behav[1], behav[-1])
            time.sleep(0.5)

            if self.clarriWay == 'pic':
                try:
                    nowPic = self.driver.screenshot()
                except:
                    nowPic = None
            else:
                try:
                    nowPic = self.driver.page_source
                except:
                    nowPic = None

            if self.CheckIsSame(nowPic, self.trueMainImg, self.mainSimiLari):  # 如果开启了这个应用检查是否一样
                # print('返回键后回归初始化状态')
                return True

        # 如果不一样或者无法跳过广告页面
        # 第四步关闭app
        # print('关闭app')
        try:
            self.driver.terminate_app(self.appName) #关闭app
        except:
            print('no need to ter') # 关闭app
        # 第五步重启

        try:
            self.driver.start_activity(self.appName, self.mainActiName)  # 检查一下能否回到这个界面？
        except:
            print('error!!')
            self.driver.press_keycode(4)
            time.sleep(0.1)
            self.driver.press_keycode(4)
            self.driver.start_activity(self.appName, self.mainActiName)  # 再开






        isStart = self.WaitXml(12)

        if (isStart):
            self.DoAct()

        if self.clarriWay == 'pic':
            try:
                nowPic = self.driver.screenshot()
            except:
                nowPic = None
        else:
            try:
                nowPic = self.driver.page_source
            except:
                nowPic = None

        print('checktrueMain', self.compXml(self.mainActiIma, self.trueMainImg))

        if isStart and self.CheckIsSame(nowPic, self.trueMainImg, self.mainSimiLari):  # 如果开启了这个应用检查是否一样
            # print('重启后初始化')
            return True

        if not isStart:
            print('waitxml error')
        else:
            print('check same 失败')

        print('初始化失败!')
        return False

    # 对某一个区域进行测试

    def DoAct(self):

        for behav in self.nowAct:
            self.DoBehav(behav[0], behav[1], behav[-1])
            print('beh', behav)

    def WaitXml(self, timeout=10):

        deadline = time.time() + timeout
        while time.time() < deadline:
            current_xml = self.driver.page_source
            # print('main wait current_xml,self.mainActiIma')
            if self.compXml(current_xml, self.mainActiIma, 0.05):
                return True
            time.sleep(.5)
        return False

    def CheckIsSame(self, firPic, secPic, simi):
        if self.clarriWay == 'pic':
            return self.compareHist(firPic, secPic, simi)
        else:
            # print('check is same!!! firPic,secPic')
            return self.compXml(firPic, secPic, simi)

    def GetTreeAllIds(self, rootNode, resultList):
        # self.uniqueID += 1

        resId = rootNode.attrib.get('bounds')  #resource-id

        if resId and resId not in resultList:
            resultList.append(resId)

        childNodes = rootNode.getchildren()
        if len(childNodes) != 0:
            for node in childNodes:
                self.GetTreeAllIds(node, resultList)

    def compXml(self, firXml, secXml, simi=0.1):
        if firXml == None:
            return secXml == None
        elif secXml == None:
            return False
        firRoot = ET.fromstring(firXml)

        secRoot = ET.fromstring(secXml)

        firIdList = []
        secIdList = []

        self.GetTreeAllIds(firRoot, firIdList)
        self.GetTreeAllIds(secRoot, secIdList)

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

        # print('diNum*1.0/saNum',diNum,saNum)
        return (diNum * 1.0 / saNum) < simi





    def GetTreeAllSpa(self, rootNode, resultList):
        # self.uniqueID += 1

        bounds = rootNode.attrib.get('bounds')
        cliAble = rootNode.attrib.get('clickable')  # clickable  scrollable
        scroAble = rootNode.attrib.get('scrollable')


        if (cliAble == "true" or scroAble == "true") and (bounds) and (bounds not in resultList):
            # if (bounds) and (bounds not in resultList):

            resultList.append((bounds,cliAble,scroAble))

        childNodes = rootNode.getchildren()
        if len(childNodes) != 0:
            for node in childNodes:
                self.GetTreeAllSpa(node, resultList)


    def ScanPage(self, cliResultList,scrResultList):

        misOpe = []

        for bound in cliResultList:

            self.timer.conStart()

            nums = re.findall(r"\d+", bound)
            # print(nums)
            lux = int(nums[0])
            luy = int(nums[1])
            rdx = int(nums[2])
            rdy = int(nums[3])

            width = rdx - lux
            height = rdy - luy

            print('width,height', width, height)
            if width < self.misTouch or height < self.misTouch:
                midX = int((lux + rdx) * 0.5)
                midY = int((luy + rdy) * 0.5)

                if self.CheckSpacingError(midX,midY,Behaviour.click):
                    misOpe.append([midX, midY])
                    # return  misOpe


            self.timer.conOver()

        for bound in scrResultList:

            self.timer.conStart()

            nums = re.findall(r"\d+", bound)
            # print(nums)
            lux = int(nums[0])
            luy = int(nums[1])
            rdx = int(nums[2])
            rdy = int(nums[3])

            width = rdx - lux
            height = rdy - luy

            print('width,height', width, height)
            if width < self.misTouch or height < self.misTouch:
                midX = int((lux + rdx) * 0.5)
                midY = int((luy + rdy) * 0.5)


                if self.CheckSpacingError(midX, midY, Behaviour.downSwipe):
                    misOpe.append([midX, midY])
                    # return misOpe

            self.timer.conOver()

        return misOpe





    def GetRom(self):

        order = 'adb shell cat /proc/meminfo'
        #
        pi = subprocess.Popen(order, shell=True, stdout=subprocess.PIPE)
        subRes = pi.stdout.read().decode('utf-8').replace("\n", " ").replace("\r", " ")



        re1 = r'MemFree:(.*?)MemAvailable:'
        theee = re.findall(re1, subRes)[0].split()[0]
        # print('theee',theee)



        # print(totalRam)


        return  theee



    def GetProcNum(self):
        order = 'adb shell ps | findstr '+self.appName+''
        #
        pi = subprocess.Popen(order, shell=True, stdout=subprocess.PIPE)
        subRes = pi.stdout.read().decode('utf-8') #.replace("\n", " ").replace("\r", " ")

        return  subRes.count(self.appName)





    def GetAllNetflow(self):


        order = 'adb shell cat /proc/net/dev'  # 获取连接设备

        pi = subprocess.Popen(order, shell=True, stdout=subprocess.PIPE)
        subRes = pi.stdout.read().decode('utf-8').replace("\n", " ").replace("\r", " ")


        # print('subRes',subRes)
        if self.netCon == 'wlan':
            re1 = r'wlan0:(.*?)[A-Za-z]'
        elif self.netCon == 'data':
            re1 = r' rmnet_data2:(.*?)[A-Za-z]'
        elif self.netCon == 'imitator':
            re1 = r' lo:(.*?) [A-Za-z]'
        theee = re.findall(re1, subRes)[0].split()
        # print('theee',theee)
        recByte = theee[0]
        subByte = theee[8]
        # print('流量')
        # print(recByte, subByte)
        return recByte, subByte








    def GetAllStatus(self):
        RecFlow,SubFlow = self.GetAllNetflow()
        ProNum = self.GetProcNum()
        Rom = self.GetRom()


        oneRec = int(RecFlow)-int(self.preRecFlow)
        oneSub = int(SubFlow)-int(self.preSubFlow)

        oneProNum = int(ProNum)-int(self.preProNum)
        oneRom = int(Rom)-int(self.preRom)


        self.preRecFlow = RecFlow
        self.preSubFlow = SubFlow
        self.preProNum = ProNum
        self.preRom = Rom

        return oneRec,oneSub,oneProNum,oneRom




    def CheckSpacingError(self,midX,midY,behv):
        self.timer.genStart()

        self.timer.navStart()
        self.CheckAndInit()
        self.timer.navOver()

        self.GetAllStatus()
        self.DoBehav(midX, midY,behv)


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

        self.timer.genOver()


        PreOneRec, PreOneSub, PreOneProNum, PreOneRom = self.GetAllStatus()




        for beh in [[midX,midY],[midX,midY]]:
            self.timer.genStart()
            self.timer.navStart()
            self.CheckAndInit()
            self.timer.navOver()

            self.GetAllStatus()
            self.DoBehav(beh[0],beh[1],behv)

            self.timer.genOver()


            self.timer.oraStart()
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

            if (not self.CheckIsSame(fir_cli_CenterImg, preActImg, self.simiLari)):
                self.AddActiToList([midX, midY, behv])
                self.timer.oraOver()
                return True

            oneRec, oneSub, oneProNum, oneRom = self.GetAllStatus()

            if (abs(oneRec-PreOneRec) > 9000 or abs(oneSub-PreOneSub) > 5000 or abs(oneProNum-PreOneProNum) > 1 or abs(oneRom-PreOneRom) > 512):
                self.timer.oraOver()
                return True

            self.timer.oraOver()

        return False






    def AddActiToList(self, act):
        try:
            acti = self.driver.page_source  # string 类型
            order = 'adb shell dumpsys window | findstr mCurrentFocus'  # 获取连接设备

            pi = subprocess.Popen(order, shell=True, stdout=subprocess.PIPE)
            subRes = pi.stdout.read().decode('utf-8').replace("\n", " ").replace("\r", " ")

            if self.appName not in subRes:
                print('not this app')
                return
            # 获取当前的activity，以及所做操作
        except:
            return

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

        action1.press(x=leX, y=cliY).wait(300).move_to(x=leX, y=diY).wait(300).release()  # .wait(1000)
        action2.press(x=cliX, y=cliY).wait(300).move_to(x=diX, y=diY).wait(300).release()  # .wait(1000)

        # 创建多点触控对象
        multi_action = MultiAction(self.driver)
        print(type(multi_action))
        # 同时执行 action1 和 action2 动作
        multi_action.add(action1)
        multi_action.add(action2)
        if isTrip:
            action3 = TouchAction(self.driver)
            action3.press(x=riX, y=cliY).wait(300).move_to(x=riX, y=diY).wait(300).release()
            multi_action.add(action3)
        # 执行多点触控
        try:
            multi_action.perform()
        except:
            print('禁止截屏！！')
        self.driver.swipe(cliX, cliY, diX, diY)



