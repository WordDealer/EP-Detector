# coding=utf-8#/usr/bin/python
#encoding:utf-8
import csv
import os
import time

#控制类
class CpuController(object):
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


class BatController(object):
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
        print(self.alldata)
        # csvfile = open('power.csv', 'wb')
        # writer = csv.writer(csvfile)
        # writer.writerows(self.alldata)
        # csvfile.close()



if __name__ == "__main__":
    controller = CpuController(10)
    controller.run()
    controller.SaveDataToCSV()

    controller = BatController(5)
    controller.run()
    controller.SaveDataToCSV()

# launchtime
# coding=utf-8
# /usr/bin/python
# encoding:utf-8
