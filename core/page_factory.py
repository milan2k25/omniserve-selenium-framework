from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.remote.webelement import WebElement
#from appium.webdriver.webelement import WebElement as m_WebElement
from selenium.webdriver.support.ui import Select
from os import path
import json
import logging
from helper import selenium_helper

class PageFactory(object):
    timeout = 5
    highlight = False

    def __init__(self):
        '''
        '''

    def __get__(self, instance, owner):
        if not instance:
            return None
        else:
            self.driver = instance.driver

    def __getattr__(self, loc):

        logging.debug(f"the current locator to be found {loc} on url {self.driver.current_url}")
        if loc in self.locators.keys():
            error = ""
            for loc_pair in self.locators[loc]:
                loc_pair[0] = selenium_helper.TYPE_OF_LOCATORS[loc_pair[0].lower()]
                loc_pair = tuple(loc_pair)
                try:
                    element = WebDriverWait(self.driver, self.timeout).until(
                        EC.presence_of_element_located(loc_pair)
                    )
                except (StaleElementReferenceException, NoSuchElementException, TimeoutException) as e:
                    error = e
                    logging.warning(f"the locator {loc} on url {self.driver.current_url} is not present")
                    continue

                try:
                    element = WebDriverWait(self.driver, self.timeout).until(
                        EC.visibility_of_element_located(loc_pair)
                    )
                except (StaleElementReferenceException, NoSuchElementException, TimeoutException) as e:
                    error = e
                    logging.warning(f"the locator {loc} on url {self.driver.current_url} is not visible")
                    continue

                element = self.get_web_element(*loc_pair)
                element._locator = loc_pair
                logging.debug(f"the locator {loc} is found!")
                return element  
            raise NoSuchElementException("An exception of type " + type(error).__name__ + " occurred. With Element -: " + loc)
        super().__getattr__(loc)

    def get_web_element(self, *loc):
        element = self.driver.find_element(*loc)
        self.highlight_web_element(element)
        return element

    def highlight_web_element(self, element):
        """
        To highlight webElement
        :param: WebElement
        :return: None
        """
        if self.highlight:
            self.driver.execute_script("arguments[0].style.border='2px ridge #33ffff'", element)

    def load_locators(self):
        """
        Loads the locators to the Page class

        The file path should be in the name of class
        Example
        class - LoginPage()
        json_file - LoginPage.json
        """
        class_name = self.__class__.__name__
        locator_path = path.join("locators",class_name + ".json")
        if path.exists(locator_path):
            with open(locator_path,) as f:
                return json.load(f)
        return {}


class ElementWrapper:
    def __init__(self) -> None:
        raise NotImplementedError("Creating an instance for this class is not allowed")
    
    def select_element_by_text(self, text):
        """
        Select webElement from dropdown list
        :param: Text of Item in dropdown
        :return: None
        """
        select = Select(self)
        select.select_by_visible_text(text)

    def select_element_by_index(self, index):
        """
        Select webElement from dropdown list
        :param: Index of Item in dropdown
        :return: None
        """
        select = Select(self)
        select.select_by_index(index)

    def select_element_by_value(self, value):
        """
        Select webElement from dropdown list
        :param: value of Item in dropdown
        :return: None
        """
        select = Select(self)
        select.select_by_value(value)

    def get_list_item_count(self):
        """
        Count of Item from Dropdown
        :param: None
        :return: count
        """
        select = Select(self)
        return len(select.options)

    def get_all_list_item(self):
        """
        Get list of Item from Dropdown
        :param: None
        :return: list of items present in dropdown
        """
        select = Select(self)
        list_item = []
        for item in select.options:
            list_item.append(item.text)
        return list_item

    def get_list_selected_item(self):
        """
        Get list of Selected item in Dropdown
        :param: None
        :return: list of items selected in dropdown
        """
        select = Select(self)
        list_item = []
        for item in select.all_selected_options:
            list_item.append(item.text)
        return list_item
    
    def get_all_elements(self):
        """
        To list all possible web elements on matching locator
        :param: None
        :return: list of all web elements
        """
        return self.find_elements(*self._locator)

    def click_button(self):
        """
        Perform  click on webElement
        :param: None
        :return: webElement
        """
        self.element_to_be_clickable()
        self.click()
        return self

    def double_click(self):
        """
        perform Double click on webElement
        :param: None
        :return: webElement
        """
        self.element_to_be_clickable()
        ActionChains(self.parent).double_click(self).perform()
        return self

    def context_click(self):
        """
        perform Right click on webElement
        :param: None
        :return: webElement
        """
        self.element_to_be_clickable()
        ActionChains(self.parent).context_click(self).perform()
        return self

    def set_text(self, value):
        """
        type text in input box
        :param: Text to be Enter
        :return: webElement
        """
        self.element_to_be_clickable()
        self.send_keys(value)
        return self

    def get_text(self):
        """
        get text from input box
        :param: None
        :return: text from webElement
        """
        return self.text

    def clear_text(self):
        """
        Clear text from EditBox
        :param: None
        :return: None
        """
        self.clear()

    def hover(self):
        """
        perform hover operation on webElement
        :param: None
        :return: None
        """
        ActionChains(self.parent).move_to_element(self).perform()

    def is_checked(self):
        """
        Check Radio button / CheckBox is selected
        :param: None
        :return: Boolean
        """
        return self.isSelected()

    def is_enabled(self):
        """
        get Enable state of webElement
        :param: None
        :return: Boolean
        """
        return self.isEnabled()

    def get_attribute(self, attribute_name):
        """
        get webElement attribute
        :param: name of Attribute
        :return: webElement attribute value
        """
        # _return self.get_attribute(attributeName)
        raise NotImplementedError()

    def w3c(self):
        return self.w3c

    def element_to_be_clickable(self, timeout=None):
        """
        Wait till the element to be clickable
        """
        if timeout is None:
            timeout = PageFactory().timeout
        return WebDriverWait(self.parent, timeout).until(
            EC.element_to_be_clickable(self._locator)
        )

    def invisibility_of_element_located(self, timeout=None):
        """
        Wait till the element to be invisible
        """
        if timeout is None:
            timeout = PageFactory().timeout
        return WebDriverWait(self.parent, timeout).until(
            EC.invisibility_of_element_located(self._locator)
        )

    def visibility_of_element_located(self, timeout=None):
        """
        Wait till the element to be visible
        """
        if timeout is None:
            timeout = PageFactory().timeout
        return WebDriverWait(self.parent, timeout).until(
            EC.visibility_of(self)
        )

    def wait_for_element_presence(self,timeout=None):
        """
        Wait till the element is present
        """
        if timeout is None:
            timeout = PageFactory().timeout
        return WebDriverWait(self.parent, timeout).until(
            EC.presence_of_element_located(self._locator)
        )

    def execute_script(self, script):
        """
        Execute JavaScript using web driver on selected web element
        :param: Javascript to be execute
        :return: None / depends on Script
        """
        return self.parent.execute_script(script, self)
    
    def is_displayed(self):
        """
        get Display state of webElement
        :param: None
        :return: Boolean
        """
        return self.isDisplayed()
    
    def scroll_to_element(self):
        """
        Execute JavaScript using web driver on selected web element
        to Scroll to View the Element
        """
        return self.parent.execute_script("arguments[0].scrollIntoView({behavior: \"auto\", block: \"center\", inline: \"center\"});", self)

    


class MobileElementWrapper(ElementWrapper):
    pass


WebElement.get_all_elements = ElementWrapper.get_all_elements
WebElement.click_button = ElementWrapper.click_button
WebElement.double_click = ElementWrapper.double_click
WebElement.context_click = ElementWrapper.context_click
WebElement.element_to_be_clickable = ElementWrapper.element_to_be_clickable
WebElement.invisibility_of_element_located = ElementWrapper.invisibility_of_element_located
WebElement.visibility_of_element_located = ElementWrapper.visibility_of_element_located
WebElement.wait_for_element_presence = ElementWrapper.wait_for_element_presence
WebElement.set_text = ElementWrapper.set_text
WebElement.get_text = ElementWrapper.get_text
WebElement.hover = ElementWrapper.hover
WebElement.clear_text = ElementWrapper.clear_text
WebElement.w3c = ElementWrapper.w3c
WebElement.is_Checked = ElementWrapper.is_checked
WebElement.is_Enabled = ElementWrapper.is_enabled
WebElement.getAttribute = ElementWrapper.get_attribute
WebElement.select_element_by_text = ElementWrapper.select_element_by_text
WebElement.select_element_by_index = ElementWrapper.select_element_by_index
WebElement.select_element_by_value = ElementWrapper.select_element_by_value
WebElement.get_list_item_count = ElementWrapper.get_list_item_count
WebElement.get_all_list_item = ElementWrapper.get_all_list_item
WebElement.get_list_selected_item = ElementWrapper.get_list_selected_item
WebElement.execute_script = ElementWrapper.execute_script
WebElement.scroll_to_element = ElementWrapper.scroll_to_element
WebElement.is_Displayed = ElementWrapper.is_displayed

"""
m_WebElement.get_all_elements = ElementWrapper.get_all_elements
m_WebElement.click_button = MobileElementWrapper.click_button
m_WebElement.double_click = MobileElementWrapper.double_click
m_WebElement.context_click = MobileElementWrapper.context_click
m_WebElement.element_to_be_clickable = MobileElementWrapper.element_to_be_clickable
m_WebElement.invisibility_of_element_located = MobileElementWrapper.invisibility_of_element_located
m_WebElement.visibility_of_element_located = MobileElementWrapper.visibility_of_element_located
m_WebElement.wait_for_element_presence = MobileElementWrapper.wait_for_element_presence
m_WebElement.set_text = MobileElementWrapper.set_text
m_WebElement.get_text = MobileElementWrapper.get_text
m_WebElement.hover = MobileElementWrapper.hover
m_WebElement.clear_text = MobileElementWrapper.clear_text
m_WebElement.w3c = MobileElementWrapper.w3c
m_WebElement.is_Checked = MobileElementWrapper.is_checked
m_WebElement.is_Enabled = MobileElementWrapper.is_enabled
m_WebElement.getAttribute = MobileElementWrapper.get_attribute
m_WebElement.select_element_by_text = MobileElementWrapper.select_element_by_text
m_WebElement.select_element_by_index = MobileElementWrapper.select_element_by_index
m_WebElement.select_element_by_value = MobileElementWrapper.select_element_by_value
m_WebElement.get_list_item_count = MobileElementWrapper.get_list_item_count
m_WebElement.get_all_list_item = MobileElementWrapper.get_all_list_item
m_WebElement.get_list_selected_item = MobileElementWrapper.get_list_selected_item
m_WebElement.execute_script = MobileElementWrapper.execute_script
m_WebElement.is_Displayed = MobileElementWrapper.is_displayed
"""