import logging,time, pytest, copy
from core.page_factory import PageFactory
from helper import selenium_helper
from pages_prod.orders_page import OrdersPage
from datetime import datetime


class NewsubductPage(PageFactory):

    def __init__(self,driver):
        # It is necessary to to initialise driver as page class member to implement Page Factory
        self.driver = driver
        #self.driver.maximize_window()
        self.locators = self.load_locators()
        self.pg_order = OrdersPage(pytest.driver)
        self.timeout = 5

    def get_next_group_date(self):
        
        if selenium_helper.is_locator_present(self.locators['next_group_start_date'],5):
            
            self.next_group_start_date.scroll_to_element()
            time.sleep(3)
            next_group_start_date = self.next_group_start_date.get_text()
            logging.info(f'Next group start date is {next_group_start_date}')
            return next_group_start_date
            
        else:
            message = "Next group Date is not visible in UI"
            return message
        
    def get_admission_close_date(self):
        if selenium_helper.is_locator_present(self.locators['admission_close_date'], 3):
            self.admission_close_date.scroll_to_element()
            time.sleep(3)
            admission_close_date = self.admission_close_date.get_text()       
            logging.info(f'Admission close date is {admission_close_date}')
            
            return admission_close_date.strip()
        
        else:
            message = 'Admission Close Date is not visible in UI'
            logging.info('Admission Close Date is not visible in UI')
            return message

    def get_countdown_time(self):
        try:
            days_left = self.admission_close_days.get_text()
            hour_left = self.admission_close_hour.get_text()
            minute_left = self.admission_close_minute.get_text()
            seconds_left = self.admission_close_second.get_text()

            logging.info(f'Day, hour, minute, and seconds are {days_left}, {hour_left}, {minute_left}, {seconds_left}')
            
            return days_left.strip(), hour_left.strip(), minute_left.strip(), seconds_left.strip()
        
        except:
            logging.info('Counter is not showing in UI')
            return None
    
    def get_next_master_group_start_date(self):
        selenium_helper.is_locator_present(self.locators['next_group_start_date'])
        self.next_group_start_date.scroll_to_element()
        date_UI = self.next_group_start_date.get_text()
        logging.info(f'Date in UI is {date_UI}')
        
        next_group_complete_date = date_UI.split(':')[1]
        logging.info(f'next_group_complete_date is {next_group_complete_date}')
        
        group_start_date = next_group_complete_date.split(' ')[1]
        group_start_month = next_group_complete_date.split(' ')[2]
        actual_month = group_start_month.replace(',', '')
        group_start_year = next_group_complete_date.split(' ')[-1]
        logging.info('group Start date, month and year are {}, {}, {}'.format(group_start_date, actual_month, group_start_year))
        return next_group_complete_date, group_start_date, actual_month, group_start_year
        
            
    def get_next_university_group_start_date(self, country_code):
        result = ''
        if selenium_helper.is_locator_present(self.locators['next_group_start_date'], 3):
            self.next_group_start_date.scroll_to_element()
            date_UI = self.next_group_start_date.get_text()
            logging.info(f'Date in UI is {date_UI}')
        
            if ':' in date_UI:
                
                splitted_date = date_UI.split(':')[1].strip()
                logging.info(f'After splitted next group date is {splitted_date}')
                
                temp_ui_date = copy.deepcopy(splitted_date)
                date_format = "%d %b, %Y"
                try:
                    result = str(bool(datetime.strptime(temp_ui_date, date_format)))
                    logging.info('Date object matched after splitted')
                except ValueError:
                    result = 'False'
                    logging.info('group start date is not matched with date format' )
                
                if result == 'True':
                    group_start_date = splitted_date.split(' ')[0]
                    group_start_month = splitted_date.split(' ')[1]
                    actual_month = group_start_month.replace(',', '')
                    group_start_year = splitted_date.split(' ')[-1]
                    logging.info('group Start date, month and year are {}, {}, {}'.format(group_start_date, actual_month, group_start_year))
                    return splitted_date, group_start_date, actual_month, group_start_year, result
            
                elif result == 'False':
                    self.pg_order.change_country(country_code)
                    time.sleep(4)
                    selenium_helper.is_locator_present(self.locators['next_group_start_date'], 3)
                    self.next_group_start_date.scroll_to_element()
                    date_UI2 = self.next_group_start_date.get_text()
                    logging.info(f'After changed country Date in UI is {date_UI2}')
                    
                    if ':' in date_UI2:
                        
                        splitted_date2 = date_UI2.split(':')[1].strip()
                        logging.info(f'After splitted date is {splitted_date2}')
                    
                        date_format = "%d %b, %Y"
                        temp_ui_date2 = copy.deepcopy(splitted_date2)
                        try:
                            result = str(bool(datetime.strptime(temp_ui_date2, date_format)))
                            logging.info('Date object matched after splited')
                        except ValueError:
                            result = 'False'
                            logging.info('group start date is not matched with date format' )
                            
                        if result == 'True':
                            group_start_date = splitted_date2.split(' ')[0]
                            group_start_month = splitted_date2.split(' ')[1]
                            actual_month = group_start_month.replace(',', '')
                            group_start_year = splitted_date2.split(' ')[-1]
                            logging.info('group Start date, month and year are {}, {}, {}'.format(group_start_date, actual_month, group_start_year))
                            return splitted_date2, group_start_date, actual_month, group_start_year, result
                        else:
                            logging.info('group start date is not present in UI')
                            return result
                        
                    elif ':' not in date_UI2:
                        
                        date_format = "%d %b, %Y"
                        temp_ui_date2 = copy.deepcopy(date_UI2)
                        try:
                            result = str(bool(datetime.strptime(temp_ui_date2, date_format)))
                            logging.info()
                        except ValueError:
                            result = 'False'
                            logging.info('group start date is not matched with date format' )
                            
                        if result == 'True':
                            group_start_date = date_UI2.split(' ')[0]
                            group_start_month = date_UI2.split(' ')[1]
                            actual_month = group_start_month.replace(',', '')
                            group_start_year = date_UI2.split(' ')[-1]
                            logging.info('group Start date, month and year are {}, {}, {}'.format(group_start_date, actual_month, group_start_year))
                            return date_UI2, group_start_date, actual_month, group_start_year, result
                        else:
                            logging.info('group start date is not present in UI')
                            return result
                        
            elif ':' not in date_UI:
                
                result = 'True'
                temp_ui_date = copy.deepcopy(date_UI)
                date_format = "%d %b, %Y"
                try:
                    result = str(bool((datetime.strptime(temp_ui_date, date_format))))
                    logging.info('Date object matched')
                except ValueError:
                    result = 'False'
                    logging.info('group start date is not matched with date format' )

                if result == 'True':
                    group_start_date = date_UI.split(' ')[0]
                    group_start_month = date_UI.split(' ')[1]
                    actual_month = group_start_month.replace(',', '')
                    group_start_year = date_UI.split(' ')[-1]
                    logging.info('group Start date, month and year are {}, {}, {}'.format(group_start_date, actual_month, group_start_year))
                    return date_UI, group_start_date, actual_month, group_start_year, result
            
                elif result == 'False':
                    self.pg_order.change_country(country_code)
                    time.sleep(4)
                    selenium_helper.is_locator_present(self.locators['next_group_start_date'], 3)
                    self.next_group_start_date.scroll_to_element()
                    date_UI2 = self.next_group_start_date.get_text()
                    logging.info(f'After changed country Date in UI is {date_UI2}')
                    
                    date_format = "%d %b, %Y"
                    temp_ui_date2 = copy.deepcopy(date_UI2)
                    try:
                        result = str(bool(datetime.strptime(temp_ui_date2, date_format)))
                        logging.info('Date object matched')
                    except ValueError:
                        result = 'False'
                        logging.info('group start date is not matched with date format' )
                        
                    if result == 'True':
                        group_start_date = date_UI2.split(' ')[0]
                        group_start_month = date_UI2.split(' ')[1]
                        actual_month = group_start_month.replace(',', '')
                        group_start_year = date_UI2.split(' ')[-1]
                        logging.info('group Start date, month and year are {}, {}, {}'.format(group_start_date, actual_month, group_start_year))
                        return date_UI2, group_start_date, actual_month, group_start_year, result
                    else:
                        logging.info('group start date is not present in UI')
                        return result
                    
        else:
            
            logging.info('Next group Start Date is not present in UI')
            result = 'Next group Date is not visible in UI'
            
            return result
                        
        
    def get_program_group_start_date(self):
        if selenium_helper.is_locator_present(self.locators['program_group_start_date'], 3):
            self.program_group_start_date.scroll_to_element()
            time.sleep(2)
            program_group_date = self.program_group_start_date.get_text()
            logging.info(f'program group date is {program_group_date}')
            
            program_group_start_date = program_group_date.split(' ')[0]
            logging.info(f'Program group start date is {program_group_start_date}')
            program_group_start_month = program_group_date.split(' ')[1]
            program_group_actual_month = program_group_start_month.replace(',', '')
            logging.info(f'Program group start month is {program_group_actual_month}')
            program_group_start_year = program_group_date.split(' ')[-1]
            logging.info(f'Program group start date is {program_group_start_year}')
            
            return program_group_date, program_group_start_date, program_group_actual_month, program_group_start_year
        else:
            return None
        
    
    def get_learning_format(self):        
        learning_type = self.learning_format.get_text()
        logging.info(f'Learning format is {learning_type}')
        
        if 'Blended Learning' in learning_type:
            return False
        else:
            return True