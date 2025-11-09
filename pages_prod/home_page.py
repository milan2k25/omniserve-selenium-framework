import logging
from core.page_factory import PageFactory
from helper import selenium_helper
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import pytest
import time
import requests
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


class HomePage(PageFactory):

    def __init__(self, driver):
        # It is necessary to to initialise driver as page class member to implement Page Factory
        self.driver = driver
        # self.driver.maximize_window()
        self.locators = self.load_locators()
        self.timeout = 5

    def load_url(self):
        try:
            # Production url
            url = pytest.config['prod_url']
            # sheldon url
            # url=pytest.config['sheldon_url']
            pytest.driver.get(url)
            time.sleep(3)
            logging.info('url loaded')
        except:
            logging.info('url not loading')
        return url

    def explore_program_CTA(self):
        counter = 0
        selenium_helper.is_locator_present(
            self.locators['btn_explore_program'], 20)
        self.btn_explore_program.click()
        time.sleep(10)
        Explore_cta = pytest.driver.current_url
        status = requests.head(Explore_cta).status_code
        if selenium_helper.is_element_present(self.locators["explore_program_verify"][0], 10) == True:
            explore_program_verify = self.explore_program_verify.get_text()
            message = 'success'
        else:
            message = 'failed'
            counter = counter+1
        return message, counter

    def explore_program_upskill_cta(self):
        self.close_all_popup()
        self.explore_program_btn.execute_script("arguments[0].click();")
        time.sleep(5)
        Explore_cta = pytest.driver.current_url
        status = requests.head(Explore_cta).status_code
        if selenium_helper.is_element_present(self.locators["category_name_skillup"][0], 10) == True:
            explore_program_verify = self.category_name_skillup.get_text()
            logging.info(f'{explore_program_verify}')
            message = 'Success'
        else:
            message = 'Failed'
            
        return message


    def explore_category_CTA(self):
        counter = 0
        time.sleep(5)
        self.btn_all_courses.click()
        time.sleep(1)
        menu_item = self.menu_item.get_text()
        logging.info(f'Menu item : {menu_item}')
        self.menu_item.hover()
        time.sleep(1)
        pytest.driver.find_element(
            By.XPATH, "(//ul[@class='sub-menu']//li//a[@title='Explore the category'])[1]").execute_script("arguments[0].click();")
        time.sleep(10)
        Explore_category_cta = pytest.driver.current_url
        logging.info(f'url loading is:{Explore_category_cta}')
        status = requests.head(Explore_category_cta).status_code
        if selenium_helper.is_element_present(self.locators["verify_category"][0], 10) == True:
            verify_caregory_heading = self.verify_category.get_text()
            logging.info(f'{verify_caregory_heading}')
            message = 'success'
        else:
            message = 'failed'
            counter = counter+1
        return counter, message

    def request_demo_CTA(self):
        counter = 0
        time.sleep(5)
        default_handle = self.driver.current_window_handle
        self.btn_request_demo.scroll_to_element()
        self.btn_request_demo.click()
        handles = list(self.driver.window_handles)
        for handle_check_counter in range(1, 10):
            if len(handles) > 1:
                time.sleep(7)
                self.driver.switch_to.window(handles[1])
                request_demo_url = pytest.driver.current_url
                status = requests.head(request_demo_url).status_code
                message = 'success'
                request_url = 'corporate-training'
                assert request_url in request_demo_url
                logging.info(f'request_demo_url is :{request_demo_url}')
                time.sleep(3)
                pytest.driver.close()
                self.driver.switch_to.window(default_handle)
            else:
                message = 'Failed'
                counter = counter+1
                break
            return counter, message

    def all_course_mega_menu(self):
        counter = 0
        time.sleep(5)
        self.btn_all_courses.click()
        time.sleep(1)
        menu_item = pytest.driver.find_elements(
            By.XPATH, "//a[@class='menu-cat']")
        for course in menu_item:
            courses = course.get_text()
            logging.info(f'{courses}')
        for i in range(1, 5):
            element = pytest.driver.find_element(
                By.XPATH, f"(//a[@class='menu-cat'])[{i}]")
            courseclickingon = element.get_text()
            ActionChains(pytest.driver).move_to_element(
                element).pause(3).perform()
            logging.info(f'course :{courseclickingon}')
            pytest.driver.find_element(
                By.XPATH, f"(//ul[@class='sub-menu']//li//a[@title='Explore the category'])[{i}]").execute_script("arguments[0].click();")
            time.sleep(10)
            course_url = pytest.driver.current_url
            logging.info(f'url loaded: {course_url}')
            status = requests.head(course_url).status_code
            logging.info(f"Status is : {status}")
            if status != 200:
                message = 'failed'
                counter = counter+1
            else:
                current_url = pytest.driver.current_url
                assert 'data-science' in current_url
            self.load_url()
            self.btn_all_courses.click()
            message = 'success'
        return counter, message

    def check_search_functionality(self):
        counter = 0
        self.close_all_popup()
        self.home_search.set_text('pg')
        time.sleep(5)
        self.home_search.send_keys(Keys.RETURN)
        time.sleep(5)
        current_url = pytest.driver.current_url
        if 'pg' in current_url:
            message = 'Success'
        else:
            counter = counter+1
            message = 'Failed'
        return counter, message

    def check_rediretion_urls_job_guarantee(self):
        counter = 0
        self.close_all_popup()
        
        if selenium_helper.is_element_present(self.locators["job_guarantee_redirection_url"][0], 10) == True:
            default_handle = self.driver.current_window_handle
            self.job_guarantee_redirection_url.click()
            time.sleep(3)
            handles = list(self.driver.window_handles)
            for handle_check_counter in range(1, 10):
                if len(handles) > 1:
                    time.sleep(7)
                    self.driver.switch_to.window(handles[1])
                    current_url = pytest.driver.current_url
                    logging.info(f"Job guarantee URL opend is : {current_url}")
                    assert 'job-guarantee' in current_url
                    message = 'success'
                else:
                    message = 'Failed'
                    counter = counter+1
                pytest.driver.close()
                self.driver.switch_to.window(default_handle)
                break
        else:
            message = 'failed'
            counter = counter+1
        return counter, message

    def check_rediretion_urls_jobs_skillup(self):
    
        message = 'Success'
        self.close_all_popup()
        
        if selenium_helper.is_element_present(self.locators["jobs_link"][0], 10):
            
            default_handle = self.driver.current_window_handle
            
            self.jobs_link.execute_script("arguments[0].click();")
            selenium_helper.wait_for_page_to_load(30, '/jobs')
            all_handles = list(self.driver.window_handles)
            
            if len(all_handles) > 1:
                time.sleep(5)
                self.driver.switch_to.window(all_handles[1])
                time.sleep(5)
                current_url = pytest.driver.current_url
                logging.info(f'Current Job Program is: {current_url}')
                
                if 'jobs' in current_url:                    
                    logging.info('Job Guarantee Url is opening')
                    
                else:
                    logging.info('Job Guarantee Url is not loading')
                    message = 'Failed'
                    
                pytest.driver.close()
                time.sleep(2)
                self.driver.switch_to.window(default_handle)
        else:
            
            message = 'Failed'
            
        return message

    def check_rediretion_urls_example_live_skillup(self):
        message = 'success'
        self.close_all_popup()
        if selenium_helper.is_element_present(self.locators["example_live_skillup"][0], 10) == True:
            default_handle = self.driver.current_window_handle
            self.example_live_skillup.click()
            selenium_helper.wait_for_page_to_load(30, 'youtube')
            handles = list(self.driver.window_handles)
            
            if len(handles) > 1:
                time.sleep(5)
                self.driver.switch_to.window(handles[1])
                current_url = pytest.driver.current_url
                logging.info(
                    f"example Live Skill Up url opend is : {current_url}")
                
                if 'youtube' in current_url:
                    message = 'success'
                else:
                    logging.info('Live Skill Up Url is not loading')
                    message = 'Failed'
                
            pytest.driver.close()
            time.sleep(2)
            self.driver.switch_to.window(default_handle)
            
        else:
            logging.info('Live Skill Up button is not present in UI')
            message = 'Failed'
            
        return message

    def check_rediretion_urls_quiz(self):
        message = 'Success'
        self.close_all_popup()
        if selenium_helper.is_element_present(self.locators["quiz"][0], 10) == True:
            default_handle = self.driver.current_window_handle
            self.quiz.click()
            selenium_helper.wait_for_page_to_load(30, '/free-quiz-skillup')
            handles = list(self.driver.window_handles)
            
            if len(handles) > 1:
                time.sleep(5)
                self.driver.switch_to.window(handles[1])
                current_url = pytest.driver.current_url
                
                if 'free-quiz-skillup' in current_url:
                    logging.info('Skill Up Quiz Url is opened successfully')
                else:
                    logging.info('Skill Up Quiz Url is not loading')
                    message = 'Failed'
                                   
                pytest.driver.close()
                time.sleep(2)
                self.driver.switch_to.window(default_handle)
            
        else:
            logging.info('Quiz button is not present in UI')
            message = 'Failed'
        
        return message

    def check_rediretion_url_free_online_course(self):
        counter = 0
        self.close_all_popup()
        if selenium_helper.is_element_present(self.locators["free_online_course"][0], 10) == True:
            default_handle = self.driver.current_window_handle
            self.free_online_course.click()
            handles = list(self.driver.window_handles)
            for handle_check_counter in range(1, 10):
                if len(handles) > 1:
                    time.sleep(7)
                    self.driver.switch_to.window(handles[1])
                    current_url = pytest.driver.current_url
                    assert 'skillup-free-online-courses' in current_url
                    message = 'success'
                else:
                    message = 'failed'
                    counter = counter+1
                pytest.driver.close()
                self.driver.switch_to.window(default_handle)
                break
        else:
            message = 'failed'
            counter = counter+1
        return counter, message

    def check_rediretion_url_Resources(self):
        
        if selenium_helper.is_element_present(self.locators["Resources"][0], 10) == True:
            default_handle = self.driver.current_window_handle
            self.Resources.click()
            selenium_helper.wait_for_page_to_load(30, '/resources')
            time.sleep(5)
            handles = list(self.driver.window_handles)
            for handle_check_counter in range(1, 10):
                if len(handles) > 1:
                    time.sleep(3)
                    self.driver.switch_to.window(handles[1])
                    current_url = pytest.driver.current_url
                    assert 'resources' in current_url
                    message = 'Success'
                else:
                    message = 'Failed'
                    
                pytest.driver.close()
                time.sleep(2)
                self.driver.switch_to.window(default_handle)
                break
        else:
            
            message = 'Failed'
        return message

    def check_rediretion_url_corporate_training(self):
        counter = 0
        
        if selenium_helper.is_locator_present(self.locators["corporate_training"], 10) == True:
            default_handle = self.driver.current_window_handle
            time.sleep(3)
            self.corporate_training.scroll_to_element()
            time.sleep(2)
            self.corporate_training.click()
            handles = list(self.driver.window_handles)
            for handle_check_counter in range(1, 10):
                if len(handles) > 1:
                    time.sleep(7)
                    self.driver.switch_to.window(handles[1])
                    current_url = pytest.driver.current_url
                    assert 'corporate-training' in current_url
                    message = 'Success'
                else:
                    message = 'failed'
                    counter = counter+1
                pytest.driver.close()
                self.driver.switch_to.window(default_handle)
                break
        else:
            message = 'Failed'
            counter = counter+1
        return counter, message

    def check_rediretion_url_example_for_business(self):
        
        message = 'Success'
        
        if selenium_helper.is_locator_present(self.locators["example_for_business"], 10) == True:
            default_handle = self.driver.current_window_handle
            time.sleep(3)
            self.example_for_business.scroll_to_element()
            time.sleep(2)
            self.example_for_business.click()
            selenium_helper.wait_for_page_to_load(30, '/business')
            time.sleep(3)
            handles = list(self.driver.window_handles)
            for handle_check_counter in range(1, 10):
                if len(handles) > 1:
                    time.sleep(3)
                    self.driver.switch_to.window(handles[1])
                    current_url = pytest.driver.current_url
                    assert 'business' in current_url
                    message = 'Success'
                else:
                    message = 'Failed'
                    counter = counter+1
                pytest.driver.close()
                time.sleep(2)
                self.driver.switch_to.window(default_handle)
                break
        else:
            
            message = 'Failed'
            
        return message

    def check_rediretion_url_become_an_instructor(self):
        
        if selenium_helper.is_element_present(self.locators["become_an_instructor"][0], 10) == True:
            default_handle = self.driver.current_window_handle
            time.sleep(2)
            self.become_an_instructor.click()
            selenium_helper.wait_for_page_to_load(30, '/become-our-trainer')
            time.sleep(3)
            handles = list(self.driver.window_handles)
            for handle_check_counter in range(1, 10):
                if len(handles) > 1:
                    time.sleep(3)
                    self.driver.switch_to.window(handles[1])
                    current_url = pytest.driver.current_url
                    assert 'become-our-trainer' in current_url
                    message = 'Success'
                else:
                    message = 'Failed'
                    counter = counter+1
                pytest.driver.close()
                time.sleep(2)
                self.driver.switch_to.window(default_handle)
                break
        else:
            message = 'Failed'
            
        return message

    def check_rediretion_url_hire_from_us(self):
        
        if selenium_helper.is_element_present(self.locators["hire_from_us"][0], 10) == True:
            default_handle = self.driver.current_window_handle
            time.sleep(2)
            self.hire_from_us.click()
            selenium_helper.wait_for_page_to_load(30, 'recruit')
            time.sleep(3)
            handles = list(self.driver.window_handles)
            for handle_check_counter in range(1, 10):
                if len(handles) > 1:
                    time.sleep(3)
                    self.driver.switch_to.window(handles[1])
                    current_url = pytest.driver.current_url
                    logging.info(f"Hire from us url Opened is: {current_url}")
                    assert 'recruit' in current_url
                    message = 'Success'
                else:
                    message = 'Failed'
                    counter = counter+1
                pytest.driver.close()
                time.sleep(2)
                self.driver.switch_to.window(default_handle)
                break
        else:
            message = 'failed'
            
        return message

    def check_login_functionality(self):
        
        self.close_all_popup()
        selenium_helper.is_locator_present(self.locators['login_page'], 10)
        self.login_page.click_button()
        selenium_helper.wait_for_page_to_load(30, '/login')
        current_url = pytest.driver.current_url
        logging.info(current_url)
        
        if 'login' in current_url:
            message = 'Success'
        else:
            message = 'Failed'
            
        return message

    def close_all_popup(self):
        
        if selenium_helper.is_locator_present(self.locators["close_button"], 12) == True:
            try:
                time.sleep(5)
                self.close_button.execute_script("arguments[0].click();")
                logging.info('Search Button Popup Appeared and clicked')
                time.sleep(2)
                action = ActionChains(pytest.driver)
                action.send_keys(Keys.ESCAPE).perform()
                time.sleep(2)
            except:
                pass
            
        if selenium_helper.is_locator_present(self.locators['close_button_iframe'], 10) == True:
            try:
                time.sleep(2)
                logging.info('Popup Iframe present')
                pytest.driver.switch_to.frame(self.close_button_iframe)
                logging.info('Inside Iframe')
                self.close_button.execute_script("arguments[0].click();")
                time.sleep(3)
                pytest.driver.switch_to.default_content()
                time.sleep(2)
            except:
                pass