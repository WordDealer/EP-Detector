# coding=utf-8#/usr/bin/python
#encoding:utf-8
import csv
import os
import time


class Controller:
    '''A controller class for monitoring CPU status.'''

    def __init__(self, count):
        '''
        Initialize the Controller.

        :param count: Number of times the test process will be executed.
        '''
        self.counter = count
        self.alldata = [('timestamp', 'cpustatus')]

    def testprocess(self):
        '''Execute a single test to get CPU status.'''
        cmd = 'adb shell "dumpsys cpuinfo | grep com.person.buddy"'
        result = os.popen(cmd)
        for line in result.readlines():
            cpuvalue = line.split('%')[0].strip()
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


class App:
    '''A class to represent an application and its interactions with adb commands.'''

    def __init__(self):
        '''Initialize App with default values.'''
        self.content = ""
        self.startTime = 0

    def LaunchApp(self):
        '''Launch the App using adb command.'''
        cmd = 'adb shell am start -W -n com.person.buddy/com.person.buddy.ui.app.LogoActivity'
        self.content = os.popen(cmd)

    def WarmStopApp(self):
        '''Warm stop the App using adb command.'''
        cmd = 'adb shell am force-stop com.person.buddy'
        os.popen(cmd)

    def ColdStopApp(self):
        '''Cold stop the App using adb command.'''
        cmd = 'adb shell am force-stop com.person.buddy'
        os.popen(cmd)

    def GetLaunchedTime(self):
        '''Get the launch time of the App from adb logs.

        Returns:
        Launch time in milliseconds.
        '''
        for line in self.content.readlines():
            if "ThisTime" in line:
                self.startTime = line.split(":")[1]
                break
        return self.startTime


class Controller:
    '''A controller class to manage multiple test processes for the App.'''

    def __init__(self, count):
        '''Initialize Controller with default values and set number of test processes.

        Args:
        count: Number of times the test process will be executed.
        '''
        self.app = App()
        self.counter = count
        self.alldata = [("timestamp", "elapsedtime")]

    def testprocess(self):
        '''Execute a single test process on the App.'''
        self.app.LaunchApp()
        time.sleep(5)
        elpasedtime = self.app.GetLaunchedTime()
        self.app.WarmStopApp()
        time.sleep(3)
        currenttime = self.getCurrentTime()
        self.alldata.append((currenttime, elpasedtime))

    def run(self):
        '''Execute the test process multiple times based on the counter.'''
        while self.counter > 0:
            self.testprocess()
            self.counter -= 1

    def getCurrentTime(self):
        '''Return the current timestamp in 'YYYY-MM-DD HH:MM:SS' format.'''
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

    def SaveDataToCSV(self):
        '''Save the collected data to a CSV file.'''
        with open('startTime2.csv', 'wb') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(self.alldata)


class Controller:
    '''A class to analyze and store data related to an application's memory usage.'''

    def __init__(self):
        '''Initialize the Controller with default values.'''
        self.alldata = [('id', 'vss', 'rss')]

    def analyzedata(self):
        '''Analyze data to extract memory usage for the application.'''
        content = self.readfile()
        i = 0
        for line in content:
            if 'com.person.buddy' in line:
                line = '#'.join(line.split())
                vss = line.split('#')[5].strip('K')
                rss = line.split('#')[6].strip('K')
                self.alldata.append((i, vss, rss))
                i += 1

    def SaveDataToCSV(self):
        '''Save the analyzed data to a CSV file.'''
        with open('meminfo.csv', 'wb') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(self.alldata)

    def readfile(self):
        '''Read and return the content of the data file.

        Returns:
        List of lines containing data.
        '''
        with open("meminfo", "r") as mfile:
            content = mfile.readlines()
        return content


class PowerController:
    '''A class to analyze and store data related to an application's power usage.'''

    def __init__(self, count):
        '''Initialize the Controller with default values.'''
        self.counter = count
        self.alldata = [('timestamp', 'power')]

    def testprocess(self):
        '''Collect power data for a single test run.'''
        result = os.popen('adb shell dumpsys battery')
        for line in result:
            if 'level' in line:
                power = line.split(':')[1]
                currenttime = self.getCurrentTime()
                self.alldata.append((currenttime, power))

    def run(self):
        '''Execute the test multiple times based on the counter.'''
        os.popen('adb shell dumpsys battery set status 1')
        while self.counter > 0:
            self.testprocess()
            self.counter -= 1
            time.sleep(30)

    def getCurrentTime(self):
        '''Return the current timestamp in 'YYYY-MM-DD HH:MM:SS' format.'''
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

    def SaveDataToCSV(self):
        '''Save the collected data to a CSV file.'''
        with open('power.csv', 'wb') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(self.alldata)


class TrafficController:
    '''A class to analyze and store data related to an application's network traffic usage.'''

    def __init__(self, count):
        '''Initialize the Controller with default values.'''
        self.counter = count
        self.alldata = [('timestamp', 'traffic')]

    def testprocess(self):
        '''Collect network traffic data for a single test run.'''
        cmd = 'adb shell "ps|grep com.person.buddy"'
        result = os.popen(cmd)
        pid = result.readlines()[0].split(' ')[5]
        traffic = os.popen('adb shell cat /proc/' + pid + '/net/dev')
        
        for line in traffic:
            line = '#'.join(line.split())
            if 'eth0' in line:
                receive = line.split('#')[1]
                transmit = line.split('#')[9]
            elif 'eth1' in line:
                receive2 = line.split('#')[1]
                transmit2 = line.split('#')[9]

        alltraffic = int(receive) + int(transmit) + int(receive2) + int(transmit2)
        alltraffic = alltraffic / 1024
        currenttime = self.getCurrentTime()
        self.alldata.append((currenttime, alltraffic))

    def run(self):
        '''Execute the test multiple times based on the counter.'''
        while self.counter > 0:
            self.testprocess()
            self.counter -= 1
            time.sleep(5)

    def getCurrentTime(self):
        '''Return the current timestamp in 'YYYY-MM-DD HH:MM:SS' format.'''
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

    def SaveDataToCSV(self):
        '''Save the collected data to a CSV file.'''
        with open('traffic.csv', 'wb') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(self.alldata)

# Example usage:
if __name__ == '__main__':
    power_controller = PowerController(5)
    power_controller.run()
    power_controller.SaveDataToCSV()
    traffic_controller = TrafficController(5)
    traffic_controller.run()
    traffic_controller.SaveDataToCSV()