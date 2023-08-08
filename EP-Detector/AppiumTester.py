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

from Step1SpaTest import Spacing
from Step2Operation import Operation

from Step3Enviromen import Enviromen
import json

from Timer import  TimeRecord

# adb shell dumpsys activity activities | findstr mResumedActivity

class TestApp():

    def __init__(self,dri):
        # self.uniqueID = 1
        self.driver = dri # 设备参数

        self.netCon = "wlan" #wlan  data  imitator
        # com.quark.browser/com.ucpro.BrowserActivity
        # com.dmzj.manhua com.eg.android.AlipayGphone
        # com.dmzj.manhua.ui.home.HomeTabsActivitys
        # com.bankcomm.Bankcomm/com.bankcomm.module.biz.home.MainActivity
        # 'com.qiyi.video', 'activity': '.WelcomeActivity
        self.appName =  None # app名字 com.eg.android.AlipayGphone    com.UCMobile
        self.mainActiName = "com.yy.hiyo.MainActivity"
         # com.eg.android.AlipayGphone.AlipayLogin   com.uc.browser.InnerUCMobile
        # mainAcitivity的名字
        self.xml = None
        self.mainXml = None
        self.actRecord = ActRecord() #记录act和activity以实现遍历
        self.nowAct = [] #从mainActivity到当前activity所需要的操作步骤
        self.simiLari = 0.7 #当前页面不操作时有滚动条，两个页面相似度
        self.waitTime = 2
        # self.mainActiIma = None #主页图片
        self.mainSimiLari = 0.8 #主页有滚动条时两个主页相似度
        self.clarriWay = 'xml' #pic xml
        self.fileCount = 0
        self.misTouch = 71
        self.isConti = True
        self.addLong = False

        self.timer = TimeRecord()







    def ScanPageForElem(self,cliResultList,scrResultList):

        try:
            image = self.driver.get_screenshot_as_base64()
   
            image = base64.b64decode(image)
            image = np.fromstring(image,np.uint8)
            image = cv2.imdecode(image,cv2.IMREAD_COLOR)

        except:
            image = None

        color = (0, 140, 255)

        space = Spacing(self)

        misOperations=  space.ScanPage(cliResultList,scrResultList)

        actiName = self.driver.current_activity

        print(misOperations)
        print('start')
        if type(image)==np.ndarray:
            for points in misOperations:
                print((points[0], points[1]))
                cv2.circle(image, (points[0], points[1]), 20, color, -1)   
                cv2.putText(image,'ableNUm'+str(self.ableConNum),(50,100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)
                cv2.putText(image,'allNUm'+str(self.allConNum),(50,200), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)


            cv2.imwrite(self.appName+'/the'+actiName+str(self.fileCount)+'scanRes.jpg', image)
            self.fileCount += 1

        print('misopee!',misOperations)



        with  open(self.appName + '/the' + actiName + str(self.fileCount) + "OpeMis.txt", "w",
                   encoding="utf-8") as file:
            fileData = json.dumps(misOperations)
            file.write(fileData)
            file.close()





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

        # 创建多点触控对象
        multi_action = MultiAction(self.driver)
        print(type(multi_action))
        # 同时执行 action1 和 action2 动作
        multi_action.add(action1)
        multi_action.add(action2)
        if isTrip:
            action3 = TouchAction(self.driver)        
            action3.press(x=riX,y=cliY).wait(300).move_to(x=riX,y=diY).wait(300).release()
            multi_action.add(action3)
        # 执行多点触控
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
        # self.uniqueID += 1

        resId = rootNode.attrib.get('bounds')

        if resId and resId not in resultList:
            resultList.append(resId)

        childNodes = rootNode.getchildren()
        if len(childNodes) != 0:
            for node in childNodes:
                self.GetTreeAllBounds(node, resultList)







    def GetTreeAllIds(self,rootNode, resultList):
        # self.uniqueID += 1

        resId = rootNode.attrib.get('bounds')  #resource-id

        if resId and resId not in resultList:
            resultList.append(resId)

        childNodes = rootNode.getchildren()
        if len(childNodes) != 0:
            for node in childNodes:
                self.GetTreeAllIds(node, resultList)


    def GetTreeAll(self,rootNode, level, cliresult,scrresult,lonresult,allList,fullList):
        # self.uniqueID += 1

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
        # self.uniqueID += 1

        bounds = rootNode.attrib.get('bounds')


        if (bounds) and (bounds not in othcliresult) and (self.IsSmallBounds(bounds,allList)):
            othcliresult.append(bounds)



        childNodes = rootNode.getchildren()
        if len(childNodes) != 0:
            for node in childNodes:
                self.AfterGetTreeAddClick(node, cliresult,allList,othcliresult,repeatLi)


    def IsSmallBounds(self,bounds,allList):
        # print('boundsssss',bounds)
        nums = re.findall(r"\d+", bounds)
        # print(nums)
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
            # print('main wait current_xml,self.mainXml')
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

        # if behavNum == 0:
        #     behavList = clickActList
        # elif behavNum == 1:
        #     behavList = downSwipeActList
        # elif behavNum == 2:
        #     behavList = otherSwipeActList



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
        order = 'adb shell dumpsys activity activities | findstr topResumedActivity'  # 获取连接设备

        pi = subprocess.Popen(order, shell=True, stdout=subprocess.PIPE)
        subRes = pi.stdout.read().decode('utf-8').replace("\n", "").replace("\r", "")
        print(subRes)
        theee = subRes.split()
        print(theee)
        fullName = theee[3].split('/')
        appName = fullName[0]
        actiName = fullName[1]
        if actiName[0] == '.':
            actiName = appName + actiName
        print(appName, actiName)
        self.appName=appName
        self.mainActiName = actiName
    def GetName2(self):
        order = 'adb shell dumpsys activity activities | findstr topResumedActivity'  # 获取连接设备

        pi = subprocess.Popen(order, shell=True, stdout=subprocess.PIPE)
        subRes = pi.stdout.read().decode('utf-8').replace("\n", "").replace("\r", "")
        print(subRes)
        theee = subRes.split()
        print(theee)
        fullName = theee[2].split('/')
        appName = fullName[0]
        actiName = fullName[1].split("}")[0]
        if actiName[0] == '.':
            actiName = appName + actiName
        print(appName, actiName)
        self.appName=appName
        self.mainActiName = actiName





    def TestAllPages(self): #总的测试函数
        dangerAction = []

        if not self.appName:
            self.GetName2()

        folder = os.path.exists(self.appName)
        if not folder:
            os.makedirs(self.appName)

        self.heit = self.driver.get_window_size()['height'] #屏幕长款
        self.widt = self.driver.get_window_size()['width']
        # print(heit, widt)




        try:
            self.driver.terminate_app(self.appName) #关闭app
        except:
            print('no need to ter')
        self.driver.start_activity(self.appName, self.mainActiName)  # 检查一下能否回到这个界面？



        self.driver.wait_activity(self.mainActiName,10)  #等待开启主页面（用于跳广告）
        # self.WaitXml(10)
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

        


        self.mainSimiLari = simiLarity-0.05



        isLoad = False

        if self.isConti:  #加载之前的内容
            isLoad,num = self.actRecord.Load(self.appName)
            self.fileCount = num
            print('befor')
        if not isLoad:
            self.actRecord.Add(self.mainActiIma,[])
            
            
            
            



        thexml,act = self.actRecord.Get()

        while thexml:
            self.timer.pageStart()
            print('not start page ')
            # print('acti',acti,'act',act)
            self.xml = thexml
            self.nowAct = act
            # d.app_start('com.dmzj.manhua')
            try:
                self.driver.terminate_app(self.appName) #关闭app
            except:
                print('no need to ter')

            try:
                self.driver.start_activity(self.appName, self.mainActiName)  # 检查一下能否回到这个界面？
            except:
                print('error!!')
                self.driver.press_keycode(4)
                time.sleep(0.1)
                self.driver.press_keycode(4)
                self.driver.start_activity(self.appName, self.mainActiName)  # 再开



            isStart = self.WaitMainXml(15)


            if (isStart):
                print('nowact', self.nowAct)
                print('doact')
                self.DoAct()
            else:
                print('not start',self.mainActiName)
            
            try:
                nowXml = self.driver.page_source
            except:
                print('get pagesource error!')
                thexml, act = self.actRecord.Get()
                continue
            
            

            if (not self.compXml(nowXml,self.xml,0.1)) :
                print('now',len(nowXml),'acti',len(self.xml))
                print('goto acti with act error!')
                thexml, act = self.actRecord.Get()
                continue

            else:
                print('goto next acti!',len(self.xml))


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

            # self.simiLari = 0.1
            if (self.simiLari > 0.3):
                print('simiError!', self.simiLari)
            # print('self simil', self.simiLari)









            root = ET.fromstring(self.trueMainImg)

            cliResultList = []
            scrResultList = []
            lonResultList = []
            allList = []
            fullList = []

            self.GetTreeAll(root, 1, cliResultList,scrResultList,lonResultList,allList,fullList)  # 获取整个界面所有元素


            self.allConNum = len(fullList)
            self.ableConNum = len(allList)

            numAllList = []
            for bd in fullList:
                nums = re.findall(r"\d+", bd)


                numAllList.append([int(nums[0]),int(nums[1]),int(nums[2]),int(nums[3])])


            if len(clickActList)<5:
                otherClResultList = []
                repeatLi = []
                self.AfterGetTreeAddClick(root, cliResultList, numAllList, otherClResultList,repeatLi)

                print('otherClResultList',otherClResultList)


                otherCliList,otherLonList = self.CheckOther(otherClResultList)

                cliResultList.extend(otherCliList)
                lonResultList.extend(otherLonList)




            print('cliResultList',cliResultList)

            self.ScanPageForElem(cliResultList,scrResultList )

            self.TestBoundsAllPagesMuiltActs(cliResultList,scrResultList,lonResultList)







            allOpeAbleList = []
            allOpeAbleList.extend(cliResultList)
            allOpeAbleList.extend(lonResultList)



            EnMisOp =  self.TestBoundsAllPagesEnviron(allOpeAbleList)

            self.actRecord.SaveEnvirEP(EnMisOp)
            # self.TestBoundsAllPages(resultList, Behaviour.tripleSwipe)
            # self.TestBoundsAllPages(resultList,Behaviour.click)

            # cliInResList = []
            # self.GetTreeAllInBounds(root, 1, resultList, cliInResList)
            #
            # cliInResList = cliInResList[:35]  # !!!!!!
            # self.TestBoundsAllPages(cliInResList,"CombieSwipe")  # 对所有边界进行测试
            self.actRecord.Save(self.appName,self.fileCount)

            self.timer.pageOver()
            thexml, act = self.actRecord.Get()


        print('dangerAction',dangerAction)


        with  open("dangerAction.txt", "w",encoding="utf-8")as file:
            file.write(str(dangerAction))
            file.close()

        self.timer.appOver(self.appName)
        
        self.actRecord.Save(self.appName,self.fileCount)

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
        # print(nums)
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
            # print('main wait current_xml,self.mainActiIma')
            if self.compXml(current_xml, self.mainActiIma, 0.05):
                return True
            time.sleep(.5)
        return False



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

        theres=self.CheckIsSame(nowPic, self.trueMainImg, self.mainSimiLari)
        print('no act:',theres)
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

        theres=self.CheckIsSame(nowPic, self.trueMainImg, self.mainSimiLari)
        print('exit act:',theres)
        if theres:
            return True

        if self.CheckIsSame(nowPic, self.trueMainImg, self.mainSimiLari): #如果开启了这个应用检查是否一样
            # print('返回键后回归初始化状态')
            return True

        if len(self.nowAct)>0:
            behav = self.nowAct[-1]
            self.DoBehav(behav[0], behav[1],behav[-1])
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


            if self.CheckIsSame(nowPic, self.trueMainImg, self.mainSimiLari): #如果开启了这个应用检查是否一样
                # print('返回键后回归初始化状态')
                return True




        #如果不一样或者无法跳过广告页面
        #第四步关闭app
        # print('关闭app')
        try:
            self.driver.terminate_app(self.appName) #关闭app
        except:
            print('no need to ter')#关闭app
        #第五步重启

        self.driver.start_activity(self.appName, self.mainActiName)  # 检查一下能否回到这个界面？

        isStart = self.WaitXml(12)


        if(isStart):
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

        print('checktrueMain',self.compXml(self.mainActiIma,self.trueMainImg))

        if isStart and self.CheckIsSame(nowPic, self.trueMainImg,self.mainSimiLari): #如果开启了这个应用检查是否一样
            # print('重启后初始化')
            return True

        if not isStart:
            print('waitxml error')
        else:
            print('check same 失败')



        print('初始化失败!')
        return False
    #对某一个区域进行测试

    def CheckIsSame(self,firPic,secPic,simi):
        if self.clarriWay == 'pic':
            return self.compareHist(firPic,secPic,simi)
        else:
            # print('check is same!!! firPic,secPic')
            return self.compXml(firPic,secPic,simi)


    def InitCheckPage(self):
        print(' ')