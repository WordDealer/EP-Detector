import time

class TimeRecord():
    def __init__(self):
        self.appTime = time.perf_counter()

        self.pageTime = 0
        self.pageNum = 0
        self.pageTimeCount = 0

        self.conTime = 0
        self.conNum = 0
        self.conTimeCount = 0

        self.genTime = 0
        self.genNum = 0
        self.genTimeCount = 0

        self.oraTime = 0
        self.oraNum = 0
        self.oraTimeCount = 0

        self.navTime = 0
        self.navNum = 0
        self.navTimeCount = 0

    def appOver(self,appname):
        self.appTime = time.perf_counter() - self.appTime

        pa = self.pageTime/self.pageNum
        co = self.conTime/self.conNum
        ge = self.genTime/self.genNum
        ora = self.oraTime/self.oraNum
        na = self.navTime/self.navNum
        with  open(appname+'/' +appname +".timeCounter.txt", "w", encoding="utf-8") as file:
            file.write('app  '+str(self.appTime)+'\n')
            file.write('page  '+str(pa)+'\n')
            file.write('page num  '+str(self.pageNum)+'\n')
            file.write('control  '+str(co)+'\n')
            file.write('con num  '+str(self.conNum)+'\n')
            file.write('genarate  '+str(ge)+'\n')
            file.write('gen num  '+str(self.genNum)+'\n')
            file.write('oracle  '+str(ora)+'\n')
            file.write('ora num  '+str(self.oraNum)+'\n')
            file.write('navigation  '+str(na)+'\n')
            file.write('na num  '+str(self.navNum)+'\n')
            file.close()

    def pageStart(self):
        self.pageTimeCount= time.perf_counter()

    def pageOver(self):
        allTime = time.perf_counter() - self.pageTimeCount
        self.pageTime += allTime
        self.pageNum += 1

    def conStart(self):
        self.conTimeCount= time.perf_counter()

    def conOver(self):
        allTime = time.perf_counter() - self.conTimeCount
        self.conTime += allTime
        self.conNum += 1

    def genStart(self):
        self.genTimeCount= time.perf_counter()

    def genOver(self):
        allTime = time.perf_counter() - self.genTimeCount
        self.genTime += allTime
        self.genNum += 1

    def oraStart(self):
        self.oraTimeCount= time.perf_counter()

    def oraOver(self):
        allTime = time.perf_counter() - self.oraTimeCount
        self.oraTime += allTime
        self.oraNum += 1

    def navStart(self):
        self.navTimeCount= time.perf_counter()

    def navOver(self):
        allTime = time.perf_counter() - self.navTimeCount
        self.navTime += allTime
        self.navNum += 1