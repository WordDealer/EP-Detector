# coding=utf-8#/usr/bin/python
#encoding:utf-8
import csv
import os
import time

#控制类
class Controller(object):
    def __init__(self, count):
        self.counter = count
        self.alldata = [("timestamp", "cpustatus")]


    #单次测试过程
    def testprocess(self):
        cmd = 'adb shell "dumpsys cpuinfo | grep com.person.buddy"'  #adb shell "dumpsys cpu|grep com.person.buddy"
       # cmd='adb shell "dumpsys cpuinfo | grep com.person.buddy"'
        result = os.popen(cmd)
        for line in result.readlines():
            cpuvalue =  line.split("%")[0]

            currenttime = self.getCurrentTime()
            self.alldata.append((currenttime, cpuvalue))

    #多次执行测试过程
    def run(self):
        while self.counter >0:
            self.testprocess()
            self.counter = self.counter - 1
            time.sleep(3)

    #获取当前的时间戳
    def getCurrentTime(self):
        currentTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        return currentTime

    #数据的存储
    def SaveDataToCSV(self):
        print(self.alldata)

        # csvfile = open('cpustatus.csv', 'wb')
        # writer = csv.writer(csvfile)
        # writer.writerows(self.alldata)
        # csvfile.close()

if __name__ == "__main__":
    controller = Controller(10)
    controller.run()
    controller.SaveDataToCSV()

# launchtime
# coding=utf-8
# /usr/bin/python
# encoding:utf-8
import csv
import os
import time


# 同QQ、微信等对比
# 同上下版本进行对比
class App(object):
    def __init__(self):
        self.content = ""
        self.startTime = 0

    # 启动App
    def LaunchApp(self):
        cmd = 'adb shell am start -W -n com.person.buddy/com.person.buddy.ui.app.LogoActivity'
        self.content = os.popen(cmd)

    # 热启动停止App
    def WarmStopApp(self):
        cmd = 'adb shell am force-stop com.person.buddy'
        # cmd = 'adb shell input keyevent 3'
        os.popen(cmd)

        # 冷启动停止APP
        def ColdStopApp(self):
            cmd = 'adb shell am force -stop com.person.buddy'
            os.open(cmd)

    # 获取启动时间
    def GetLaunchedTime(self):
        for line in self.content.readlines():
            if "ThisTime" in line:
                self.startTime = line.split(":")[1]
                break
        return self.startTime


# 控制类
class Controller(object):
    def __init__(self, count):
        self.app = App()
        self.counter = count
        self.alldata = [("timestamp", "elapsedtime")]

    # 单次测试过程
    def testprocess(self):
        self.app.LaunchApp()
        time.sleep(5)
        elpasedtime = self.app.GetLaunchedTime()
        self.app.WarmStopApp()
        time.sleep(3)
        currenttime = self.getCurrentTime()
        self.alldata.append((currenttime, elpasedtime))

    # 多次执行测试过程
    def run(self):
        while self.counter > 0:
            self.testprocess()
            self.counter = self.counter - 1

    # 获取当前的时间戳
    def getCurrentTime(self):
        currentTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        return currentTime

    # 数据的存储
    def SaveDataToCSV(self):
        csvfile = open('startTime2.csv', 'wb')
        writer = csv.writer(csvfile)
        writer.writerows(self.alldata)
        csvfile.close()


if __name__ == "__main__":
    controller = Controller(10)
    controller.run()
    controller.SaveDataToCSV()

# men
# coding=utf-8
#/usr/bin/python
#encoding:utf-8
import csv
import os
import  time

#控制类
class Controller(object):
    def __init__(self):
        #定义收集数据的数组
        self.alldata = [("id", "vss", "rss")]

    #分析数据
    def analyzedata(self):
        content = self.readfile()
        i = 0
        for line in content:
            if "com.person.buddy" in line:
                print (line)
                line = "#".join(line.split())
                vss = line.split("#")[5].strip("K")
                rss = line.split("#")[6].strip("K")

                #将获取到的数据存到数组中
                self.alldata.append((i, vss, rss))
                i = i + 1

    #数据的存储
    def SaveDataToCSV(self):
        csvfile = open('meminfo.csv', 'wb')
        writer = csv.writer(csvfile)
        writer.writerows(self.alldata)
        csvfile.close()

    #读取数据文件
    def readfile(self):
        mfile = open("meminfo", "r")
        content = mfile.readlines()
        mfile.close()
        return  content

if __name__ == "__main__":
    controller = Controller()
    controller.analyzedata()
    controller.SaveDataToCSV()

# power
# coding=utf-8
#/usr/bin/python
#encoding:utf-8
import csv
import os
import time

#控制类
class Controller(object):
    def __init__(self, count):
        #定义测试的次数
        self.counter = count
        #定义收集数据的数组
        self.alldata = [("timestamp", "power")]

    #单次测试过程
    def testprocess(self):
        #执行获取电量的命令
        result = os.popen("adb shell dumpsys battery")
        #获取电量的level
        for line in result:
            if "level" in line:
                power = line.split(":")[1]

        #获取当前时间
        currenttime = self.getCurrentTime()
        #将获取到的数据存到数组中
        self.alldata.append((currenttime, power))

    #多次测试过程控制
    def run(self):
        #设置手机进入非充电状态
        os.popen("adb shell dumpsys battery set status 1")
        while self.counter >0:
            self.testprocess()
            self.counter = self.counter - 1
            #每30秒钟采集一次数据
            time.sleep(30)

    #获取当前的时间戳
    def getCurrentTime(self):
        currentTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        return currentTime

    #数据的存储
    def SaveDataToCSV(self):
        csvfile = open('power.csv', 'wb')
        writer = csv.writer(csvfile)
        writer.writerows(self.alldata)
        csvfile.close()

if __name__ == "__main__":
    controller = Controller(5)
    controller.run()
    controller.SaveDataToCSV()
#traffic
# coding=utf-8
#/usr/bin/python
#encoding:utf-8
import csv
import os
import string
import time

#控制类
class Controller(object):
    def __init__(self, count):
        #定义测试的次数
        self.counter = count
        #定义收集数据的数组
        self.alldata = [("timestamp", "traffic")]

    #单次测试过程
    def testprocess(self):
        #执行获取进程的命令
        cmd = 'adb shell "ps|grep com.person.buddy"'
        result = os.popen(cmd)
        #获取进程ID
        pid = result.readlines()[0].split(" ")[5]

        #获取进程ID使用的流量
        traffic = os.popen("adb shell cat /proc/"+pid+"/net/dev")
        for line in traffic:
            if "eth0" in line:
                #将所有空行换成#
                line = "#".join(line.split())
                #按#号拆分,获取收到和发出的流量
                receive = line.split("#")[1]
                transmit = line.split("#")[9]
            elif "eth1" in line:
                # 将所有空行换成#
                line =  "#".join(line.split())
                # 按#号拆分,获取收到和发出的流量
                receive2 = line.split("#")[1]
                transmit2 = line.split("#")[9]

        #计算所有流量的之和
        alltraffic = string .atoi(receive) + string .atoi(transmit) + string .atoi(receive2) + string .atoi(transmit2)
        #按KB计算流量值
        alltraffic = alltraffic/1024
        #获取当前时间
        currenttime = self.getCurrentTime()
        #将获取到的数据存到数组中
        self.alldata.append((currenttime, alltraffic))

    #多次测试过程控制
    def run(self):
        while self.counter >0:
            self.testprocess()
            self.counter = self.counter - 1
            #每5秒钟采集一次数据
            time.sleep(5)

    #获取当前的时间戳
    def getCurrentTime(self):
        currentTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        return currentTime

    #数据的存储
    def SaveDataToCSV(self):
        csvfile = open('traffic.csv', 'wb')
        writer = csv.writer(csvfile)
        writer.writerows(self.alldata)
        csvfile.close()

if __name__ == "__main__":
    controller = Controller(5)
    controller.run()
    controller.SaveDataToCSV()