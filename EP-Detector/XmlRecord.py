import copy
from xml.etree import ElementTree as ET
import json
from behaviour import Behaviour
class ActRecord():
    def __init__(self):
        self.undTesActiID = -1
        self.activityList = []
        self.actList = []
        self.EnPageList = []
    
    def GetTreeAll(self,rootNode, level, resultList):
        # self.uniqueID += 1

        bounds = rootNode.attrib.get('bounds')
        cliAble = rootNode.attrib.get('clickable')  #clickable  scrollable
        if cliAble=="true" and bounds and bounds not in resultList:
            resultList.append(bounds)

        childNodes = rootNode.getchildren()
        if len(childNodes) != 0:
            for node in childNodes:
                self.GetTreeAll(node, level + 1, resultList)


    def compXml(self,firXml,secXml):
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


        return (diNum*1.0/saNum)<0.2


    def GetTreeAllIds(self,rootNode, resultList):

        resId = rootNode.attrib.get('bounds')  #resource-id

        if resId and resId not in resultList:
            resultList.append(resId)

        childNodes = rootNode.getchildren()
        if len(childNodes) != 0:
            for node in childNodes:
                self.GetTreeAllIds(node, resultList)
    def Add(self, activity, act):
        '''
        Check if an activity is in the list. If not, add it.
        Also, record the associated operation.
        
        Args:
        - activity: The XML representation of the activity.
        - act: The associated action for the activity.
        '''
        
        isRepe = False
        for xml in self.activityList:
            if self.compXml(activity, xml):
                isRepe = True
                break  

        if not isRepe:
            if self.undTesActiID == -1:
                temp = []
            else:
                temp = copy.deepcopy(self.actList[self.undTesActiID])
                temp.append(act)
            self.activityList.append(activity)
            self.actList.append(temp)
            print('After appending:')
            print(len(self.activityList), self.actList)

    def Get(self):
        '''
        Increment the undTesActiID and retrieve the corresponding activity and action.
        
        Returns:
        - tuple: The activity and its corresponding action or (None, None) if out of range.
        '''
        self.undTesActiID += 1
        if self.undTesActiID < len(self.activityList):
            return self.activityList[self.undTesActiID], self.actList[self.undTesActiID]
        else:
            return None, None

    def Save(self, appName, fileCount):
        '''
        Save the app's activities and actions to a file.
        
        Args:
        - appName: The name of the app.
        - fileCount: The file count for naming.
        '''
        numActList = copy.deepcopy(self.actList)
        for i in range(len(numActList)):
            for j in range(len(numActList[i])):
                numActList[i][j][2] = numActList[i][j][2].value
        theData = {'appName': appName, 'undTesActiID': self.undTesActiID, 'ativiLi': self.activityList, 'actLi': numActList, 'fileCount': fileCount}
        with open("theData.txt", "w", encoding="utf-8") as file:
            file.write(json.dumps(theData))

    def SaveEnvirEP(self, EnMisOp):
        '''
        Save the environment endpoint and related data to a file.
        
        Args:
        - EnMisOp: The environment missing operation.
        '''
        self.EnPageList.append({'actiId': self.undTesActiID, 'enMisOp': EnMisOp})
        with open("theEnvFile.txt", "w", encoding="utf-8") as file:
            file.write(json.dumps(self.EnPageList))

    def LoadEnvirEP(self):
        '''
        Load the environment endpoint data from a file.
        '''
        with open("theEnvFile.txt", "r", encoding="utf-8") as file:
            theData = json.loads(file.read())
            self.EnPageList = theData

    def Load(self,appName):
        with  open("theData.txt", "r",encoding="utf-8")as file:
            theData = file.read()
            theData = json.loads(theData)

            if not theData:
                print('data null')
                return False,0
            elif appName != theData['appName']:
                print('not the app')
                return False,0
            elif theData['undTesActiID'] == -1:
                print('at start page')
                return False,0
            else:
                self.undTesActiID = theData['undTesActiID']-1
                self.activityList = theData['ativiLi']
                fileCount = theData['fileCount']
                numActList = theData['actLi']
                for i in range(len(numActList)):
                    for j in range(len(numActList[i])):
                        numActList[i][j][2] = Behaviour(int(numActList[i][j][2])) 
                self.actList = numActList
                self.LoadEnvirEP()
                print('loaded!')
                return True,fileCount