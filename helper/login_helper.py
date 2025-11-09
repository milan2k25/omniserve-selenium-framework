import  pytest
import time
from pages.meta_functionality_page import MetaFunctionalityPage
from pages.home_page import HomePage
from pages.login_page import LoginPage
from helper import selenium_helper
def __init__(self, driver):
        self.driver = driver
        self.driver.maximize_window()
        self.locators = self.load_locators()
        self.timeout = 10

def login():
    pytest.driver.get(pytest.config['url'])

def university_login():
    pytest.driver.get(pytest.config['university_url'])

def new_url_login():
    pytest.driver.get(pytest.config['new_url'])

def group_url_login():
    pytest.driver.get(pytest.config['group_url'])

def backend_admin_login(email,password):
    pytest.driver.get(pytest.config['backend_ui_docker']+pytest.config['backend_ui_docker'])
    pg_backend = MetaFunctionalityPage(pytest.driver)
    #Step3 : Enter email and password and click on login button
    pg_backend.login_simplex(email,password)

def grow_signUp():
    pytest.driver.get(pytest.config['sheldon_docker']+pytest.config['grow_url'])
    selenium_helper.wait_for_page_to_load(30, pytest.config['grow_url'])
    time.sleep(3)

def grow_referral_signUp():
    pytest.driver.get(pytest.config['sheldon_docker']+pytest.config['grow_referral_url'])
    selenium_helper.wait_for_page_to_load(30, pytest.config['grow_referral_url'])
    time.sleep(3)

def grow_certificate_signUp():
    pytest.driver.get(pytest.config['sheldon_docker']+pytest.config['grow_certificate_url'])
    selenium_helper.wait_for_page_to_load(30, pytest.config['grow_certificate_url'])
    time.sleep(3)

def logout():
    pg_home = HomePage(pytest.driver)
    pg_home.logout()

def grow_logout():
    pg_home = HomePage(pytest.driver)
    pg_home.grow_logout()

def chusagc_admin_login(email,password):
    pg_login = LoginPage(pytest.driver)
    pytest.driver.get(pytest.config['hufdghf_docker']+pytest.config['chusagc_login_url'])
    pg_login.login(email, password)

def chusagc_admin_logout():
    pg_login = LoginPage(pytest.driver)
    pg_login.chusagc_admin_logout()
    
def sheldon_dynamic_url(required_url):
    url = pytest.config['sheldon_docker']+required_url
    pytest.driver.get(url)
    selenium_helper.wait_for_page_to_load(60,required_url)

def chusagc_prod_login(email,password):
    pg_login = LoginPage(pytest.driver)
    pytest.driver.get(pytest.config['prod_chusagc_login_url'])
    pg_login.login(email, password)