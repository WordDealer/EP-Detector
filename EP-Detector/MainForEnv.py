import time

from appium import webdriver

from AppiumTesterForEnv import  TestApp

if __name__ == '__main__':

    # Device configuration
    desc = {
        'deviceName': '127.0.0.1:69abe452',   # Device name (e.g., emulator-5554, 291af785 from 'adb devices')
        'platformVersion': '13',               # Phone version (found in: Settings -> About Phone on device)
        'platformName': 'Android'              # Device type (iOS or Android)
    }

    ''' 
    Command to get app information:
    apt dump badging C:\Users\83473\Desktop\mobileqq_android.apk
    '''

    # Initialize the webdriver. If Appium isn't properly installed, you can use Appium-Desktop as an alternative.
    driver = webdriver.Remote('http://127.0.0.1:4723/wd/hub', desc)

    # Testing the application's pages
    test = TestApp(driver)
    test.TestAllPages()

    print("Main for env finished")
