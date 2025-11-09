from distutils.log import error
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import Select
from os import path
import json
import logging
import pytest, shutil,os

TYPE_OF_LOCATORS = {
    'css': By.CSS_SELECTOR,
    'css selector': By.CSS_SELECTOR,
    'id': By.ID,
    'name': By.NAME,
    'xpath': By.XPATH,
    'link_text': By.LINK_TEXT,
    'partial_link_text': By.PARTIAL_LINK_TEXT,
    'tag': By.TAG_NAME,
    'class_name': By.CLASS_NAME
}

def wait_for_page_to_load(timeout,url):
    try:
        WebDriverWait(pytest.driver, timeout).until(EC.url_contains(url))
    except TimeoutException:
        pass

def is_element_present(loc_pair, timeout=5):
    loc_pair[0] = TYPE_OF_LOCATORS[loc_pair[0].lower()]
    if not isinstance(loc_pair, tuple):
        loc_pair = tuple(loc_pair)
    
    try:
        WebDriverWait(pytest.driver, timeout).until(
            EC.presence_of_element_located(loc_pair)
        )
        return True
    except (StaleElementReferenceException, NoSuchElementException, TimeoutException) as e:
        logging.error(e)
        #logging.warning(f"the locator {loc_pair} on url {pytest.driver.current_url} is not present")
    return False

def is_element_visible(loc_pair, timeout=5):
    loc_pair[0] = TYPE_OF_LOCATORS[loc_pair[0].lower()]
    if not isinstance(loc_pair, tuple):
        loc_pair = tuple(loc_pair)
    
    try:
        WebDriverWait(pytest.driver, timeout).until(
            EC.visibility_of_element_located(loc_pair)
        )
        return True
    except (StaleElementReferenceException, NoSuchElementException, TimeoutException) as e:
        logging.error(e)
        logging.warning(f"the locator {loc_pair} on url {pytest.driver.current_url} is not visible")
    return False



def scroll_page(pixels:str):
    """
    Execute JavaScript using web driver on selected web element
    to Scroll the Page Up or Down
    :param: pixels (positive number to scroll down, negative number to scroll up)
    """
    return pytest.driver.execute_script("window.scrollBy(0, " + pixels + ");")

def accept_alert(timeout=5):
    try:
        WebDriverWait(pytest.driver, timeout).until(EC.alert_is_present(),
                                    'Timed out waiting for PA creation ' +
                                    'confirmation popup to appear.')

        alert = pytest.driver.switch_to.alert
        alert.accept()
        logging.info("Alert Accepted")
    except TimeoutException:
        raise TimeoutException ("No Alert Found")

def execute_script(script):
    """
        Execute JavaScript using web driver on page
        :param: Javascript to be execute
        :return: None / depends on Script
    """
    return pytest.driver.execute_script(script)

def scroll_to_page_bottom():
        """
        Execute JavaScript using web driver on selected web element
        to Scroll to Bottom of the page
        """
        return pytest.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
def is_element_clickable(loc_pair, timeout=5):
    loc_pair[0] = TYPE_OF_LOCATORS[loc_pair[0].lower()]
    if not isinstance(loc_pair, tuple):
        loc_pair = tuple(loc_pair)
    
    try:
        WebDriverWait(pytest.driver, timeout).until(
            EC.element_to_be_clickable(loc_pair)
        )
        return True
    except (StaleElementReferenceException, NoSuchElementException, TimeoutException, Exception ) as e:
        logging.error(e)
        logging.warning(f"the locator {loc_pair} on url {pytest.driver.current_url} is not visible")
    return False

def is_locator_present(loc, timeout = 5):
    length = len(loc)
    is_locator_present = False
    for i in range(0, length):
        if is_element_present(loc[i], timeout):
            is_locator_present = True
            break
    return is_locator_present
    
def is_locator_clickable(loc, timeout = 5):
    length = len(loc)
    is_locator_clickable = False
    for i in range(0, length):
        if is_element_clickable(loc[i], timeout):
            is_locator_clickable = True
            break
    return is_locator_clickable

def clear_all_screenshot():
    # Remove all existing screenshots Screenshot
    try:
        shutil.rmtree("report\screenshot")
        
    except:
        print("No Directory Found with Name : report\screenshot")
        pass
        
    try:
        os.makedirs(os.path.dirname(os.curdir).join("report\screenshot"),exist_ok=True)
    except:
        pass

def wait_till_element_to_invisible(locator,timeout=5):
    
    locator_invisibility = False

    for index in range(0,len(locator)):
        locator[index][0] = TYPE_OF_LOCATORS[locator[index][0].lower()]

        if not isinstance(locator[index], tuple):
            loc_pair = tuple(locator[index])

        try:
            if WebDriverWait(pytest.driver, timeout).until(
                    EC.invisibility_of_element_located(loc_pair)):
                locator_invisibility = True
                return locator_invisibility
            
        except (StaleElementReferenceException, TimeoutException) as e:
            logging.error(e)
            logging.warning(f"the locator {loc_pair} on url {pytest.driver.current_url} is still present")
    return locator_invisibility