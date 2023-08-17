# coding=utf-8#/usr/bin/python
#encoding:utf-8
import csv
import os
import time

import os
import time

class CpuController:
    '''A controller class for monitoring CPU status.'''

    def __init__(self, count):
        '''
        Initialize the CpuController.

        :param count: Number of times the test process will be executed.
        '''
        self.counter = count
        self.alldata = [('timestamp', 'cpustatus')]

    def testprocess(self):
        '''Execute a single test to get CPU status.'''
        cmd = 'adb shell "dumpsys cpuinfo | grep com.person.buddy"'
        result = os.popen(cmd)
        for line in result.readlines():
            cpuvalue = line.split('%')[0]
            currenttime = self.getCurrentTime()
            self.alldata.append((currenttime, cpuvalue))

    def run(self):
        '''Execute the test multiple times based on the counter.'''
        while self.counter > 0:
            self.testprocess()
            self.counter -= 1
            time.sleep(3)

    def getCurrentTime(self):
        '''Return the current timestamp in 'YYYY-MM-DD HH:MM:SS' format.'''
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

    def SaveDataToCSV(self):
        '''Print the collected data. Intended to save to CSV in the future.'''
        print(self.alldata)
        # Uncomment below lines to save data to CSV
        # csvfile = open('cpustatus.csv', 'wb')
        # writer = csv.writer(csvfile)
        # writer.writerows(self.alldata)
        # csvfile.close()


class BatController:
    '''A controller class for monitoring battery status.'''

    def __init__(self, count):
        '''
        Initialize the BatController.

        :param count: Number of times the test process will be executed.
        '''
        self.counter = count
        self.alldata = [('timestamp', 'power')]

    def testprocess(self):
        '''Execute a single test to get battery status.'''
        result = os.popen("adb shell dumpsys battery")
        for line in result:
            if "level" in line:
                power = line.split(':')[1].strip()
                currenttime = self.getCurrentTime()
                self.alldata.append((currenttime, power))

    def run(self):
        '''Execute the test multiple times based on the counter.'''
        os.popen("adb shell dumpsys battery set status 1")
        while self.counter > 0:
            self.testprocess()
            self.counter -= 1
            time.sleep(30)

    def getCurrentTime(self):
        '''Return the current timestamp in 'YYYY-MM-DD HH:MM:SS' format.'''
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

    def SaveDataToCSV(self):
        '''Print the collected data. Intended to save to CSV in the future.'''
        print(self.alldata)
        # Uncomment below lines to save data to CSV
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
