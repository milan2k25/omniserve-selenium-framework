from interface import implements, Interface
from selenium import webdriver
#from appium import webdriver as m_webdriver
from msedge.selenium_tools import options as EdgeOptions
from msedge.selenium_tools import webdriver as EdgeWebdriver

def driver_manager_factory(d_type):
    d_type = d_type.lower()
    if d_type in ['chrome','chromedriver']:
        return ChromeDriverManager()
    elif d_type in ['firefox','geckodriver']:
        return FirefoxDriverManager()
    elif d_type in ['edge']:
        return EdgeDriverManager()
    elif d_type in ['ie']:
        return InternetExplorerDriverManager()
    elif d_type in ['safari','safaridriver']:
        return SafariDriverManager()
    elif d_type in ['m_safari','safari_mobile']:
        return SafariMobileDriverManager()
    elif d_type in ['m_chrome','chrome_mobile']:
        return ChromeMobileDriverManager()
    else:
        return FirefoxDriverManager()


# ! Driver executable are need to be added in PATH variable
# ! Path/URL of the Appium Server should come from a config [Start on desired url and port] TODO
# ! Desired Capabilities of mobile can also come from a config
class DriverManager(Interface):

    def __init__(self):
        '''
        Initiate the WebDriver Executable Path and Desired Capabilities
        '''
        pass

    def create_driver(self):
        '''
        Create Web Driver
        '''
        pass


# Note: Add 'geckodriver' executable as PATH variable
class FirefoxDriverManager(implements(DriverManager)):

    def __init__(self):
        self.driver = None

    def create_driver(self):
        #firefox_profile = webdriver.FirefoxProfile()
        #firefox_profile.set_preference("browser.privatebrowsing.autostart", True)
        #firefox_options = webdriver.FirefoxOptions()
        #firefox_options.headless = True
        #firefox_options.add_argument("--width=1920")
        #firefox_options.add_argument("--width=1080")
        #self.driver = webdriver.Firefox(firefox_profile=firefox_profile, options=firefox_options)
        self.driver = webdriver.Firefox()
        self.driver.maximize_window()
        return self.driver


# Note: Add 'chromedriver' executable as PATH variable
class ChromeDriverManager(implements(DriverManager)):

    def __init__(self):
        self.driver = None

    def create_driver(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--incognito")
        #chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
        #For mobile view enable this
        #mobile_emulation = { "deviceName": "Moto G4" }
        #chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
        self.driver = webdriver.Chrome(options=chrome_options)
        #self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        return self.driver


class SafariDriverManager(implements(DriverManager)):

    def __init__(self):
        self.driver = None

    def create_driver(self):
        self.driver = webdriver.Safari()
        self.driver.maximize_window()
        return self.driver


# Note: Add 'msedgedriver' executable as PATH variable
class EdgeDriverManager(implements(DriverManager)):

    def __init__(self):
        self.driver = None

    def create_driver(self):
        options= EdgeOptions.Options()
        options.use_chromium = True
        options.add_argument("headless")
        options.add_argument("disable_gpu")

        #cap = webdriver.DesiredCapabilities().EDGE
        #cap["platform"] = "ANY"
        
        #self.driver = webdriver.Edge("msedgedriver",capabilities=cap)
        self.driver = EdgeWebdriver.WebDriver(options=options)
        #self.driver.maximize_window()
        self.driver.set_window_size(1920, 1080)
        return self.driver


# Note: Add 'ie' executable as PATH variable
class InternetExplorerDriverManager(implements(DriverManager)):

    def __init__(self):
        self.driver = None

    def create_driver(self):
        raise NotImplementedError


# Note: iOS Simulator or Real Device need to be connected and available
class SafariMobileDriverManager(implements(DriverManager)):

    def __init__(self,capabilities = None):
        self.dc = capabilities
        self.driver = None
        # Todo Launch Appium Server if not running
        # ! Desired capabilities should come from config.ini [Framework specific config]

    def create_driver(self):
        dc = {
            "platformName": "iOS",
            "platformVersion": "13.6",
            "deviceName": "iPad Pro",
            "automationName": "XCUITest",
            "browserName": "Safari",
            "udid":'CC853F55-AB84-48E8-AEB5-39FE56E721DB'
        }   
        self.driver = m_webdriver.Remote('http://localhost:4723/wd/hub',dc)
        return self.driver


# Note: Android Emulator or Real Device need to be connected and available
class ChromeMobileDriverManager(implements(DriverManager)):

    def __init__(self,capabilities = None):
        self.dc = capabilities
        self.driver = None

    def create_driver(self):
        options = webdriver.ChromeOptions()
        options.add_experimental_option('androidPackage', 'com.android.chrome')
        self.driver = webdriver.Chrome('chromedriver', options=options)
        return self.driver