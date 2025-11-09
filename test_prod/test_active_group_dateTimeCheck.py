import logging
import pytest
import csv
import os
import time
import datetime
import pandas
import re
import copy
from pages_prod.new_subduct_page import NewsubductPage
from pages_prod.orders_page import OrdersPage
from helper import selenium_helper
from helper.database import db_helper
from operator import itemgetter


class TestNewsubductgroupTimeCheck():

    @pytest.fixture
    def initialize_pages(self, scope='class'):
        self.pg_new_subduct = NewsubductPage(pytest.driver)
        self.pg_order = OrdersPage(pytest.driver)

    def _test_add_rows_in_csv():
        '''
        Remove Existing report.CSV file and Crete a new one,
        Remove Screenshot directory inside report
        '''

        # Create Report.CSV File
        try:
            os.remove("Report.csv")
        except OSError:
            pass

        # Create Report.CSV file
        with open('Report.csv', 'w', newline='\n') as fp:
            f = csv.writer(fp)
            f.writerow(["Page Type", "URL", 'Next group Date', 'Admission Close Date/Program Induction Date',
                       'Days', 'Hours', 'Minutes', 'Seconds', 'group Status', 'Welcome Class Status', 'Status'])
    
    # Getting New subduct URL from DB
    def _get_newsubduct_url():

        new_subdoamin_query = '''SELECT Concat("https://", u.university_domain, seo.url) AS un_url
                        FROM   prion.university u
                                JOIN prion.university_mapping um
                                        ON u.university_id = um.university_id
                                JOIN prion.seo
                                        ON um.linkable_id = seo.linkable_id
                                INNER JOIN prion.landingPageContents AS lc
                                        ON lc.linkable_id = prion.seo.linkable_id
                        WHERE  prion.seo.controller = 'university-domain'
                        AND um.status = 1 and lc.is_new_template = 1
                        GROUP  BY un_url;'''

        db_data = db_helper.get_prod_data(new_subdoamin_query)
        urls = list(map(itemgetter('un_url'), db_data))

        return urls

    # Getting Old subduct URL from DB
    def _get_Oldsubduct_url():

        old_subduct_query = '''SELECT Concat("https://", u.university_domain, seo.url) AS un_url
                        FROM   prion.university u
                                JOIN university_mapping um
                                        ON u.university_id = um.university_id
                                JOIN seo
                                        ON um.linkable_id = seo.linkable_id
                                INNER JOIN prion.landingPageContents AS lc
                                        ON lc.linkable_id = seo.linkable_id
                        WHERE u.university_domain not like '%onlinebootcamp.ce.uci.edu%'
                        and u.university_domain not like '%bootcamp.viterbiexeced.usc.edu%'
                        and seo.url not like '%design-thinking-certification-training-online-course%'
                        and seo.controller = 'university-domain'
                        AND um.status = 1 and lc.is_new_template = 0
                        GROUP  BY un_url;'''

        db_data = db_helper.get_prod_data(old_subduct_query)
        urls = list(map(itemgetter('un_url'), db_data))

        return urls

    # Verifying UI class date in DB by picking date from UI and getting bundle ID from URL
    def verify_UI_class_date_from_DB(self, ui_date, seo_url):

        logging.info(f'Convert UI Date into timestamp is {ui_date}')
        converted_timestamp = datetime.datetime.strptime(ui_date, "%d %b, %Y")
        logging.info(
            f'After converted date to timestamp is {converted_timestamp} ')
        db_date_format = converted_timestamp.strftime('%Y-%m-%d')
        logging.info(f'DB date format is {db_date_format}')

        query_to_fetch_group_date = f'''
            select count(*) as count from jupiter.class 
                    where class_dates like '%{db_date_format}%'
                        and class_status = 'active'
                        and program_id = (select linkable_id from prion.seo where url = '/{seo_url}' 
                        and linkable_id is not null);'''

        logging.info(
            f'Query to fetch group date is {query_to_fetch_group_date}')
        db_data_for_date = db_helper.get_prod_data(query_to_fetch_group_date)
        logging.info(f'Fetch date from db {db_data_for_date}')
        cls_date = list(map(itemgetter('count'), db_data_for_date))
        logging.info(f"Class Date is present in DB {cls_date}")

        return cls_date
    
    # Verifying UI class date in DB by adding one more day in UI date and getting bundle ID from URL
    def verify_UI_class_date_from_DB_after_converted(self, ui_date, seo_url):
        
        logging.info(f'Convert UI Date into timestamp is {ui_date}')
        temp_date_obj = datetime.datetime.strptime(ui_date, "%d %b, %Y")
        logging.info(
            f'After converted date to timestamp is {temp_date_obj} ')
        
        # temp_date_obj = datetime.datetime.fromtimestamp(temp_timestamp)
        one_day = datetime.timedelta(days=1)
        new_temp_timestamp = temp_date_obj + one_day
        logging.info(f'After one day added new date is {new_temp_timestamp}')
        db_date_format = new_temp_timestamp.strftime('%Y-%m-%d')
        logging.info(f'After converted new timestamp is {db_date_format}')

        query_to_fetch_group_date2 = f'''
            select count(*) as count from jupiter.class 
            where class_dates like '%{db_date_format}%'
                and class_status = 'active'
                and program_id = (select linkable_id from prion.seo where url = '/{seo_url}' 
                and linkable_id is not null);'''

        logging.info(
            f'Query to fetch group date is {query_to_fetch_group_date2}')
        db_data_for_date2 = db_helper.get_prod_data(query_to_fetch_group_date2)
        logging.info(f'Fetch date from db after converted {db_data_for_date2}')
        cls_date2 = list(map(itemgetter('count'), db_data_for_date2))
        logging.info(f"After converted class Date is present in DB {cls_date2}")
        
        return cls_date2
        
    # Verifying group is present in DB or not for specific program by getting bundle ID from URL
    def verify_group_from_DB(self, seo_url):

        query_to_fetch_no_of_group = f'''select count(group_ai_id) as count 
                                                    from jupiter.group where status = 1 
                                                    and is_deprecated = 0 
                                                    and program_id = (select linkable_id from prion.seo where url = '/{seo_url}');'''

        # logging.info(f'DB query for check group details {query_to_fetch_no_of_group}')
        db_data_for_group = db_helper.get_prod_data(
            query_to_fetch_no_of_group)
        logging.info(f'Data from db for group is {db_data_for_group}')
        no_of_group = list(map(itemgetter('count'), db_data_for_group))
        logging.info(f'Number of group present for program is {no_of_group}')

        return no_of_group

    # Verifying Class is present or not in DB for specific Program group
    def verify_welcome_class_from_DB(self, seo_url):

        query_to_fetch_no_of_welcome_class = f'''
                select count(jcl.group_id) as count
                            from jupiter.group as jco inner join jupiter.class as jcl
                                on jco.group_ai_id = jcl.group_id
                            where jco.program_id = (select linkable_id from prion.seo where url = '/{seo_url}')
                            and jcl.program_id = (select linkable_id from prion.seo where url = '/{seo_url}')
                                and jco.status = 1
                                and jco.is_deprecated = 0
                                and jcl.is_welcome = 1
                                and jcl.class_status = 'active'
                                and jcl.class_dates > curdate();'''

        # logging.info(f'DB query for check welcome class details {query_to_fetch_no_of_welcome_class}')
        db_data_for_cls = db_helper.get_prod_data(
            query_to_fetch_no_of_welcome_class)
        logging.info(f'Data from db for class is {db_data_for_cls}')
        no_of_class = list(map(itemgetter('count'), db_data_for_cls))
        logging.info(
            f'Number of welcome class present for program is {no_of_class}')

        return no_of_class


    _test_add_rows_in_csv()
    @pytest.mark.test_details("SLUB-T0001", "high", "New subduct", "Om")
    @pytest.mark.parametrize("url", _get_newsubduct_url())
    def test_new_subduct_coohort_time_check(self, url, initialize_pages):

        message = 'Passed'
        group_status = 'NA'
        welcome_class_status = 'NA'

        logging.info(f'New sub domain url is {url}')
        pytest.driver.get(url)
        selenium_helper.wait_for_page_to_load(5, url)
        
        seo_url = url.split('/')[-1]

        # Getting Next group date
        next_group_start_date = self.pg_new_subduct.get_next_group_date()
        logging.info(f'Next group start date: {next_group_start_date}')
        
        # Getting admission close date
        admission_close_date = self.pg_new_subduct.get_admission_close_date()
        logging.info(f'Admission close date: {admission_close_date}')
        
        # Getting counter value
        counter_value = self.pg_new_subduct.get_countdown_time()
        
        # Verifying if next group start date, admission close date and counter value is not present
        if 'not visible in UI' in next_group_start_date and 'not visible in UI' in admission_close_date and counter_value == None:
            
            current_url = pytest.driver.current_url
            logging.info(f'After Redirected Current URL is {current_url}')
            
            # Verifying whether current url is matching with actual url or not
            if current_url != url:
                
                logging.info('Actual URL is redirected to different URL')
                message = 'Failed'

                rows = [["Sub Domain New Template", f'Actual URL is {url} and redirection url is {current_url}', next_group_start_date, admission_close_date,
                        'NA', 'NA', 'NA', 'NA', group_status, welcome_class_status, message]]
                with open("Report.csv", 'a', newline='\n') as csvfile:
                    csvwriter = csv.writer(csvfile)
                    csvwriter.writerows(rows)
                    
                pytest.fail('Actual URL is redirected to different URL')
                
            # Verifying group and welcome class is exist or not in DB, if Next group date, Admission Close date and counter value is not present in UI
            else:
            
                logging.info('Next group date, Admission Close date and Counter value is not showing in UI')
                
                no_of_group = self.verify_group_from_DB(seo_url)

                if no_of_group[0] >= 1:

                    group_status = 'group is present'

                    no_of_class = self.verify_welcome_class_from_DB(seo_url)

                    if no_of_class[0] >= 1:
                        
                        welcome_class_status = 'Welcome class is present for the program'
                        message = 'Failed'

                    else:
                        welcome_class_status = 'Welcome class is not present for the program'
                        message = 'Passed'

                else:
                    group_status = 'No groups Available'
                    message = 'Passed'

                rows = [["Sub Domain New Template", url, next_group_start_date, admission_close_date, 'Null',
                            'Null', 'Null', 'Null', group_status, welcome_class_status,
                            message]]
                
                with open("Report.csv", 'a', newline='\n') as csvfile:
                    csvwriter = csv.writer(csvfile)
                    csvwriter.writerows(rows)
                
                if 'Failed' in message:
                    pytest.fail('Next group date and Admission close date is not visible in UI')
                                    
        # Verifying UI class date is correct or not from DB, if Next group date, admission close date and counter value is present in UI
        else:
            
            result = True
            
            try:
                result = bool(datetime.datetime.strptime(
                    next_group_start_date, "%d %b, %Y"))
                logging.info('Date object matched')
            except ValueError:
                result = False
                logging.info('Date Object is not matched')

            if result == True:

                cls_date = self.verify_UI_class_date_from_DB(
                    next_group_start_date, seo_url)

                if cls_date[0] >= 1:

                    logging.info('group date is showing correct in UI')
                    group_status = 'group is present'
                    welcome_class_status = 'Welcome class date is matched'
                    
                elif cls_date[0] == 0:
                    
                    logging.info('group date is not matched with UI')
                
                    cls_date2 = self.verify_UI_class_date_from_DB_after_converted(next_group_start_date, seo_url)
                
                    if cls_date2[0] >= 1:
                        
                        logging.info('group date is showing correct in UI after converted')
                        group_status = 'group is present'
                        welcome_class_status = 'Welcome class date is matched after converted'
                        
                    else:
                        
                        welcome_class_status = 'Welcome class date is mismatched after converted'
                        message = 'Failed'
                        logging.info('Incorrect group date is showing in UI after converted')

                else:
                    welcome_class_status = 'Welcome class date is mismatched'
                    message = 'Failed'
                    logging.info('Incorrect group date is showing in UI')

            date = next_group_start_date.split(',')[0].split(' ')[0]
            month = next_group_start_date.split(',')[0].split(' ')[1]

            # logging.info(next_group_start_date)
            # logging.info(date)
            # logging.info(month)
            # logging.info(admission_close_date)
            # logging.info(f'Day, hour, minute, seconds are {days_left}, {hour_left}, {minute_left}, {seconds_left}')

            if date not in admission_close_date and month not in admission_close_date:
                message = 'Failed'

            if 'Admission Closes On' not in admission_close_date:
                message = 'Failed'

            if counter_value[0] == '0' and counter_value[1] == '0' and counter_value[2] == '0' and counter_value[3] == '0':

                no_of_group = self.verify_group_from_DB(seo_url)

                if no_of_group[0] >= 1:

                    group_status = 'group is present'

                    no_of_class = self.verify_welcome_class_from_DB(seo_url)

                    if no_of_class[0] >= 1:
                        welcome_class_status = 'Welcome class is present for the program'
                        message = 'Failed'

                    else:
                        welcome_class_status = 'Welcome class is not present for the program'
                        message = 'Passed'

                else:
                    group_status = 'No groups Available'
                    message = 'Passed'

            rows = [["Sub Domain New Template", url, next_group_start_date, admission_close_date,
                    counter_value[0], counter_value[1], counter_value[2], counter_value[3], group_status, welcome_class_status, message]]
            with open("Report.csv", 'a', newline='\n') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerows(rows)

            if 'Failed' in message:
                pytest.fail('Failed')


    _test_add_rows_in_csv()
    @pytest.mark.test_details("SLUB-T0002", "high", "Old subduct", "Om")
    @pytest.mark.parametrize("url", _get_Oldsubduct_url())
    def test_old_subduct_coohort_time_check(self, url, initialize_pages):

        message = 'Passed'
        group_status = 'NA'
        welcome_class_status = 'NA'

        pytest.driver.delete_all_cookies()
        logging.info(f'Old sub domain url is {url}')        
        pytest.driver.get(url)
        selenium_helper.wait_for_page_to_load(5, url)

        # Getting Admission close date from UI
        admission_close_date = self.pg_new_subduct.get_admission_close_date()

        # Getting Counter Value from UI
        counter_value = self.pg_new_subduct.get_countdown_time()

        seo_url = url.split('/')[-1]
        
        # Verifying if Admission close date and Counter Value is not present in UI
        if 'not visible in UI' in admission_close_date and counter_value == None:
            
            current_url = pytest.driver.current_url
            logging.info(f'After Redirected Current URL is {current_url}')
            
            # Verifying whether current url is matching with actual url or not
            if current_url != url:
                
                logging.info('Actual URL is redirected to different URL')
                message = 'Failed'

                rows = [["Sub Domain Old Template", f'Actual URL is {url} and redirection url is {current_url}',
                         'Null', admission_close_date, 'NA', 'NA', 'NA', 'NA', group_status,
                         welcome_class_status, message]]
                with open("Report.csv", 'a', newline='\n') as csvfile:
                    csvwriter = csv.writer(csvfile)
                    csvwriter.writerows(rows)
                    
                pytest.fail('Actual URL is redirected to different URL')
            
            # Verifying group and welcome class is exist or not in DB, if Next group date, Admission Close date and counter value is not present in UI
            else:
            
                logging.info('Admission Close date and Counter value is not showing in UI')
                    
                no_of_group = self.verify_group_from_DB(seo_url)

                if no_of_group[0] >= 1:

                    group_status = 'group is present'

                    no_of_class = self.verify_welcome_class_from_DB(seo_url)

                    if no_of_class[0] >= 1:
                        
                        welcome_class_status = 'Welcome class is present for the program'
                        message = 'Failed'

                    else:
                        welcome_class_status = 'Welcome class is not present for the program'
                        message = 'Passed'

                else:
                    group_status = 'No groups Available'
                    message = 'Passed'

                rows = [["Sub Domain Old Template", url, 'Null', admission_close_date, 'Null',
                            'Null', 'Null', 'Null', group_status, welcome_class_status,
                            message]]
                
                with open("Report.csv", 'a', newline='\n') as csvfile:
                    csvwriter = csv.writer(csvfile)
                    csvwriter.writerows(rows)
                    
                if 'Failed' in message:
                    
                    pytest.fail('Admission Close Date and Counter is not showing in UI')
        
        # Verifying group and welcome class is correct or not from DB, if Next group date, Admission Close date and counter value is present in UI
        elif 'ADMISSION CLOSED' not in admission_close_date:

            # Adding current year with UI date as Year is not showing in UI
            temp = admission_close_date.split(' ')
            current_year = '2023'
            temp_lst = []
            new_date_format = (re.sub(r"[^0-9]", "", temp[-2]))

            if len(new_date_format) == 1:

                temp_lst.append(f'0{new_date_format}')

            else:
                temp_lst.append(new_date_format)

            new_month = temp[-1]
            temp_lst.append(f'{new_month},')
            temp_lst.append(current_year)
            new_ui_date = ' '.join(temp_lst)
            logging.info(f'After formatted new date is {new_ui_date}')

            cls_date = self.verify_UI_class_date_from_DB(new_ui_date, seo_url)

            if cls_date[0] >= 1:

                logging.info('group date is showing correct in UI')
                group_status = 'group is present'
                welcome_class_status = 'Welcome class date is matched'
                
            elif cls_date[0] == 0:
                
                logging.info('group date is not matched with UI')
                
                cls_date2 = self.verify_UI_class_date_from_DB_after_converted(new_ui_date, seo_url)
                
                if cls_date2[0] >= 1:
                    
                    logging.info('group date is showing correct in UI after converted')
                    group_status = 'group is present'
                    welcome_class_status = 'Welcome class date is matched after converted'
                    
                else:
                    
                    group_status = 'group is present'
                    welcome_class_status = 'Welcome class date is mismatched after converted'
                    message = 'Failed'
                    logging.info('Incorrect group date is showing in UI after converted')

            else:
                
                group_status = 'No groups Available'
                welcome_class_status = 'Welcome class date is mismatched'
                message = 'Failed'
                logging.info('Incorrect group date is showing in UI')

            rows = [["Sub Domain Old Template", url, 'Null', admission_close_date, counter_value[0],
                     counter_value[1], counter_value[2], counter_value[3], group_status, welcome_class_status, message]]
            with open("Report.csv", 'a', newline='\n') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerows(rows)
            
            if 'Failed' in message:
                pytest.fail()

        # Verifying group and welcome class is exist or not in DB, if Next group date, Admission Close date and counter value is not present in UI
        elif counter_value[0] == '0' and counter_value[1] == '0' and counter_value[2] == '0' and counter_value[3] == '0' and 'ADMISSION CLOSED' in admission_close_date:

            no_of_group = self.verify_group_from_DB(seo_url)

            if no_of_group[0] >= 1:

                group_status = 'group is present'

                no_of_class = self.verify_welcome_class_from_DB(seo_url)

                if no_of_class[0] >= 1:

                    welcome_class_status = 'Welcome class is present for the program'
                    message = 'Failed'

                else:
                    welcome_class_status = 'Welcome class is not present for the program'
                    message = 'Passed'

            else:
                group_status = 'No groups Available'
                message = 'Passed'

            rows = [["Sub Domain Old Template", url, 'Null', admission_close_date, counter_value[0],
                     counter_value[1], counter_value[2], counter_value[3], group_status, welcome_class_status, message]]
            with open("Report.csv", 'a', newline='\n') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerows(rows)

        if 'Failed' in message:
            
            pytest.fail()

    def _get_groupMaster_urls():
        url = []
        with open('group_master_prod.csv', encoding='utf-8') as csvf:
            csvReader = csv.DictReader(csvf)
            for i in csvReader:
                url.append(i['id'])
        return url


    _test_add_rows_in_csv()
    @pytest.mark.test_details("SLUB-T0003", "high", "group Master", "Om")
    @pytest.mark.parametrize("value", _get_groupMaster_urls())
    def test_group_master_date_check(self, value, initialize_pages):

        message = 'Passed'
        global result
        group_status = 'NA'
        welcome_class_status = 'NA'
        page_type = 'group Master'

        pytest.driver.delete_all_cookies()

        df = pandas.read_csv("group_master_prod.csv", on_bad_lines='skip')
        data = df[df['id'] == value]

        url_value = data['url'].values[0]
        logging.info(F'group master URL is {url_value}')
        country_value = data['country_code'].values[0]
        # logging.info(f'Country code are {country_value}')

        pytest.driver.get(url_value)

        selenium_helper.wait_for_page_to_load(5, url_value)
        
        # Getting Next group date
        result = self.pg_new_subduct.get_next_university_group_start_date(
            country_value)

        seo_url = url_value.split('/')[-1]
        
        # Verifying if next group start date is not present
        if 'not visible in UI' in result:
            
            current_url = pytest.driver.current_url
            logging.info(f'After Redirected Current URL is {current_url}')
            
            # Verifying whether current url is matching with actual url or not
            if current_url != value:
                
                logging.info('Actual URL is redirected to different URL')
                message = 'Failed'

                rows = [[page_type, f'Actual URL is {value} and redirection url is {current_url}',
                         result, 'Null','NA', 'NA', 'NA', 'NA', group_status,
                         welcome_class_status, message]]
                with open("Report.csv", 'a', newline='\n') as csvfile:
                    csvwriter = csv.writer(csvfile)
                    csvwriter.writerows(rows)
                    
                pytest.fail('Actual URL is redirected to different URL')
            
            # Verifying group and welcome class is exist or not in DB, if Next group date is not present in UI
            else:
                
                logging.info('group Master Next group Date is not present in UI')
                
                no_of_group = self.verify_group_from_DB(seo_url)

                if no_of_group[0] >= 1:

                    group_status = 'group is present'

                    no_of_class = self.verify_welcome_class_from_DB(seo_url)

                    if no_of_class[0] >= 1:

                        welcome_class_status = 'Welcome class is present for the program'
                        message = 'Failed'

                    else:
                        welcome_class_status = 'Welcome class is not present for the program'
                        message = 'Passed'

                else:
                    group_status = 'No groups Available'
                    message = 'Passed'

                rows = [[page_type, value, result, 'Null', 'NA',
                        'NA', 'NA', 'NA', group_status, welcome_class_status, message]]
                with open("Report.csv", 'a', newline='\n') as csvfile:
                    csvwriter = csv.writer(csvfile)
                    csvwriter.writerows(rows)
                    
                if 'Failed' in message:
                    
                    pytest.fail('Next group date is not showing in UI!!!')

        # Verifying UI class date is exist or not in DB, if Next group date is not present in UI
        elif result == 'False':

            no_of_group = self.verify_group_from_DB(seo_url)

            if no_of_group[0] >= 1:

                group_status = 'group is present'

                no_of_class = self.verify_welcome_class_from_DB(seo_url)

                if no_of_class[0] >= 1:

                    welcome_class_status = 'Welcome class is present for the program'
                    message = 'Failed'

                else:
                    welcome_class_status = 'Welcome class is not present for the program'
                    message = 'Passed'

            else:
                group_status = 'No groups Available'
                message = 'Passed'

            rows = [[page_type, url_value, 'NA', 'NA', 'NA', 'NA',
                     'NA', 'NA', group_status, welcome_class_status, message]]
            with open("Report.csv", 'a', newline='\n') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerows(rows)
                
            if 'Failed' in message:
                pytest.fail('Next group date is not present in UI!!!')

        # Verifying UI class date is correct or not from DB, if Next group date, admission close date and counter value is present in UI
        elif result[-1] == 'True':

            cls_date = self.verify_UI_class_date_from_DB(result[0], seo_url)

            if cls_date[0] >= 1:

                logging.info('Next group date is showing correct in UI')
                group_status = 'group is present'
                welcome_class_status = 'Welcome class date is matched'
                
            elif cls_date[0] == 0:
                
                logging.info('group date is not matched with UI')
                
                cls_date2 = self.verify_UI_class_date_from_DB_after_converted(result[0], seo_url)
                
                if cls_date2[0] >= 1:
                
                    logging.info('group date is showing correct in UI after converted')
                    group_status = 'group is present'
                    welcome_class_status = 'Welcome class date is matched after converted'
                
                else:
                    
                    welcome_class_status = 'Welcome class date is mismatched after converted'
                    message = 'Failed'
                    logging.info('Incorrect group date is showing in UI after converted')

            else:
                welcome_class_status = 'Welcome class date is mismatched'
                message = 'Failed'
                logging.info('Incorrect group date is showing in UI')

            # Verifying if program group date is showing in UI or not
            program_group_details = self.pg_new_subduct.get_program_group_start_date()
            logging.info(
                f'Program groups details is {program_group_details}')

            if program_group_details == None:
                message = 'Program groups section not shown in UI'

                rows = [[page_type, url_value, result[0], 'Null',
                         'NA', 'NA', 'NA', 'NA', 'NA', 'NA', message]]
                with open("Report.csv", 'a', newline='\n') as csvfile:
                    csvwriter = csv.writer(csvfile)
                    csvwriter.writerows(rows)

                pytest.fail('Program groups section not shown in UI!!!')

            if result[1] == '0' and len(result[2]) >= 3 and len(result[3]) >= 2:
                message = 'Failed'

            if program_group_details[1] != result[1] and program_group_details[2] != result[2] and program_group_details[3] != result[3]:
                message = 'Failed'

            rows = [[page_type, url_value, result[0], program_group_details[0],
                     'NA', 'NA', 'NA', 'NA', group_status, welcome_class_status, message]]
            # logging.info(f'write data is {rows}')
            with open("Report.csv", 'a', newline='\n') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerows(rows)

            if 'Failed' in message:
                pytest.driver.get_screenshot_as_file(os.path.join(os.path.dirname(
                    os.curdir), "report\screenshot", f"{__name__}_{datetime.datetime.now().timestamp()}.jpeg"))
                pytest.fail()


    def _get_new_pg_template_urls():
        
        pg_new_template_query = '''
            SELECT concat("https://example.com",url) as template_url FROM prion.seo where status=1 
				and linkable_type="bundle" 
                and url not like '%testbundle%'
                and url not like '/test%'
                and url not like '%-test'
                and controller="purdue-masters" 
                and params like '%"is_university_program":true%';'''

        db_data_urls = db_helper.get_prod_data(pg_new_template_query)
        urls = list(map(itemgetter('template_url'), db_data_urls))
        
        return urls
        
        # field_names = ['template_url', 'country_id']
        
        # Open the CSV file in write mode and write the data to it
        # with open('pg_new_templates_urls.csv', 'w', newline='\n') as csvfile:
        #     writer = csv.DictWriter(csvfile, fieldnames=field_names)
        #     writer.writeheader()  # write the header row with column names
        #     for row in db_data_urls:
        #         writer.writerow(row)  # write each row of data to the CSV file

        # # Return the first column of data as input for pytest parameterize function
        # input_values = [row['template_url'] for row in db_data_urls]
        # return input_values


    _test_add_rows_in_csv()
    @pytest.mark.test_details("SLUB-T0004", "high", "PG New Template", "Om")
    @pytest.mark.parametrize("value", _get_new_pg_template_urls())
    def test_pg_new_template_date_check(self, value, initialize_pages, testdata):

        message = 'Passed'
        global result
        global program_group_details
        group_status = 'NA'
        welcome_class_status = 'NA'
        page_type = 'PG New Template'

        pytest.driver.delete_all_cookies()

        pytest.driver.get(value)
        selenium_helper.wait_for_page_to_load(5, value)
        logging.info(f'PG new template URLs is {value}')

        result = self.pg_new_subduct.get_next_university_group_start_date(testdata['country_value'])
        logging.info(f'Values are {result} and type is {type(result)}')

        seo_url = value.split('/')[-1]
        
        # Verifying if next group start date is not visible in UI
        if 'not visible in UI' in result:
            
            current_url = pytest.driver.current_url
            logging.info(f'After Redirected Current URL is {current_url}')
            
            # Verifying if Actual URL is redirected to different url or not
            if current_url != value:
                
                logging.info('Actual URL is redirected to different URL')
                message = 'Failed'

                rows = [[page_type, f'Actual URL is {value} and redirection url is {current_url}',
                         result, 'Null','NA', 'NA', 'NA', 'NA', group_status,
                         welcome_class_status, message]]
                with open("Report.csv", 'a', newline='\n') as csvfile:
                    csvwriter = csv.writer(csvfile)
                    csvwriter.writerows(rows)
                    
                pytest.fail('Actual URL is redirected to different URL')
            
            # Verifying group and welcome class is exist or not in DB, if Next group date is not present in UI
            else:
                
                logging.info('New Template Next group Date is not present in UI')
                
                no_of_group = self.verify_group_from_DB(seo_url)

                if no_of_group[0] >= 1:

                    group_status = 'group is present'

                    no_of_class = self.verify_welcome_class_from_DB(seo_url)

                    if no_of_class[0] >= 1:

                        welcome_class_status = 'Welcome class is present for the program'
                        message = 'Failed'

                    else:
                        welcome_class_status = 'Welcome class is not present for the program'
                        message = 'Passed'

                else:
                    group_status = 'No groups Available'
                    message = 'Passed'

                rows = [[page_type, value, result, 'Null', 'NA',
                        'NA', 'NA', 'NA', group_status, welcome_class_status, message]]
                with open("Report.csv", 'a', newline='\n') as csvfile:
                    csvwriter = csv.writer(csvfile)
                    csvwriter.writerows(rows)
                    
                if 'Failed' in message:
                    
                    pytest.fail('Next group date is not showing in UI!!!')

        # Verifying UI class date is exist or not in DB, if Next group date is not present in UI
        elif result == 'False':

            no_of_group = self.verify_group_from_DB(seo_url)

            if no_of_group[0] >= 1:

                group_status = 'group is present'

                no_of_class = self.verify_welcome_class_from_DB(seo_url)

                if no_of_class[0] >= 1:

                    welcome_class_status = 'Welcome class is present for the program'
                    message = 'Failed'

                else:
                    welcome_class_status = 'Welcome class is not present for the program'
                    message = 'Passed'

            else:
                group_status = 'No groups Available'
                message = 'Passed'

            rows = [[page_type, value, 'Null', 'Null', 'NA',
                     'NA', 'NA', 'NA', group_status, welcome_class_status, message]]
            with open("Report.csv", 'a', newline='\n') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerows(rows)
                
            if 'Failed' in message:
                
                pytest.fail('Next group date is not showing in UI!!!')

        # Verifying UI class date is correct or not from DB, if Next group date is present in UI
        elif result[-1] == 'True':

            cls_date = self.verify_UI_class_date_from_DB(result[0], seo_url)

            if cls_date[0] >= 1:

                logging.info('Next group date is showing correct in UI')
                group_status = 'group is present'
                welcome_class_status = 'Welcome class date is matched'
                
            elif cls_date[0] == 0:
                
                logging.info('group date is not matched with UI')
                
                cls_date2 = self.verify_UI_class_date_from_DB_after_converted(result[0], seo_url)
                
                if cls_date2[0] >= 1:
                    
                    logging.info('group date is showing correct in UI after converted')
                    group_status = 'group is present'
                    welcome_class_status = 'Welcome class date is matched after converted'
                    
                else:
                    
                    group_status = 'group is present'
                    welcome_class_status = 'Welcome class date is mismatched after converted'
                    message = 'Failed'
                    logging.info('Incorrect group date is showing in UI after converted')

            else:
                
                group_status = 'No groups Available'
                welcome_class_status = 'Welcome class date is mismatched'
                message = 'Failed'
                logging.info('Incorrect group date is showing in UI')
            
            # Verifying if Learning Format is 'Blended Learning' or not
            res = self.pg_new_subduct.get_learning_format()
            
            if res == True:

                program_group_details = self.pg_new_subduct.get_program_group_start_date()
                logging.info(
                    f'Program groups details is {program_group_details}')

                if program_group_details is not None:

                    if result[1] == '0' and len(result[2]) >= 3 and len(result[3]) >= 2:
                        message = 'Failed'

                    if program_group_details[1] != result[1] and program_group_details[2] != result[2] and program_group_details[3] != result[3]:
                        message = 'Failed'

                    rows = [[page_type, value, result[0], program_group_details[0],
                            'NA', 'NA', 'NA', 'NA', group_status, welcome_class_status, message]]
                    # logging.info(f'write data is {rows}')
                    with open("Report.csv", 'a', newline='\n') as csvfile:
                        csvwriter = csv.writer(csvfile)
                        csvwriter.writerows(rows)
                        
                    if 'Failed' in message:
                        pytest.fail()
                    
            else:
                
                if result[1] == '0' and len(result[2]) >= 3 and len(result[3]) >= 2:
                    message = 'Failed'

                rows = [[page_type, value, result[0], 'NA',
                        'NA', 'NA', 'NA', 'NA', group_status, welcome_class_status, message]]
                # logging.info(f'write data is {rows}')
                with open("Report.csv", 'a', newline='\n') as csvfile:
                    csvwriter = csv.writer(csvfile)
                    csvwriter.writerows(rows)

                if 'Failed' in message:
                    pytest.fail()
                    

    
    def _get_old_pg_template_urls():

        pg_old_template_query = '''
            SELECT concat("https://example.com",url) as template_url FROM prion.seo where status=1
                and url not like '%test-bundle%'
                and url not like '/test%'
                and url not like '%-test'
                and url not like '%getting-started-with-pgc-data-science%'
				and linkable_type="bundle"
                and controller="purdue-masters" 
                and params not like '%"is_university_program":true%';'''

        db_data_urls = db_helper.get_prod_data(pg_old_template_query)
        urls = list(map(itemgetter('template_url'), db_data_urls))
        
        return urls
        
        # field_names = ['template_url', 'country_id']
        
        # # Open the CSV file in write mode and write the data to it
        # with open('pg_old_templates_urls.csv', 'w', newline='\n') as csvfile:
        #     writer = csv.DictWriter(csvfile, fieldnames=field_names)
        #     writer.writeheader()  # write the header row with column names
        #     for row in db_data_urls:
        #         writer.writerow(row)  # write each row of data to the CSV file

        # # Return the first column of data as input for pytest parameterize function
        # input_values = [row['template_url'] for row in db_data_urls]
        # return input_values


    _test_add_rows_in_csv()
    @pytest.mark.test_details("SLUB-T0005", "high", "PG Old Template", "Om")
    @pytest.mark.parametrize("value", _get_old_pg_template_urls())
    def test_pg_old_template_date_check(self, value, initialize_pages, testdata):

        message = 'Passed'
        global result
        global program_group_details
        group_status = 'NA'
        welcome_class_status = 'NA'
        page_type = 'PG Old Template'

        pytest.driver.delete_all_cookies()

        pytest.driver.get(value)
        selenium_helper.wait_for_page_to_load(5, value)
        logging.info(f'PG old template URLs is {value}')

        result = self.pg_new_subduct.get_next_university_group_start_date(testdata['country_value'])
        logging.info(f'Values are {result} and type is {type(result)}')

        seo_url = value.split('/')[-1]
        
        # Verifying if next group start date is not visible in UI
        if 'not visible in UI' in result:
            
            current_url = pytest.driver.current_url
            logging.info(f'After Redirected Current URL is {current_url}')
            
            # Verifying if Actual URL is redirected to different url or not            
            if current_url != value:
                
                logging.info('Actual URL is redirected to different URL')
                message = 'Failed'

                rows = [[page_type, f'Actual URL is {value} and redirection url is {current_url}',
                         result, 'Null','NA', 'NA', 'NA', 'NA', group_status,
                         welcome_class_status, message]]
                with open("Report.csv", 'a', newline='\n') as csvfile:
                    csvwriter = csv.writer(csvfile)
                    csvwriter.writerows(rows)
                    
                pytest.fail('Actual URL is redirected to different URL')
            
            # Verifying group and welcome class is exist or not in DB, if Next group date is not present in UI
            else:
                
                logging.info('Old Template Next group Date is not present in UI')
                
                no_of_group = self.verify_group_from_DB(seo_url)

                if no_of_group[0] >= 1:

                    group_status = 'group is present'

                    no_of_class = self.verify_welcome_class_from_DB(seo_url)

                    if no_of_class[0] >= 1:

                        welcome_class_status = 'Welcome class is present for the program'
                        message = 'Failed'

                    else:
                        welcome_class_status = 'Welcome class is not present for the program'
                        message = 'Passed'

                else:
                    group_status = 'No groups Available'
                    message = 'Passed'

                rows = [[page_type, value, 'Null', 'Null', 'NA',
                        'NA', 'NA', 'NA', group_status, welcome_class_status, message]]
                with open("Report.csv", 'a', newline='\n') as csvfile:
                    csvwriter = csv.writer(csvfile)
                    csvwriter.writerows(rows)
                    
                if 'Failed' in message:
                    
                    pytest.fail('Next group date is not showing in UI!!!')

        # Verifying UI class date is exist or not in DB, if Next group date is not present in UI
        elif result == 'False':

            no_of_group = self.verify_group_from_DB(seo_url)

            if no_of_group[0] >= 1:

                group_status = 'group is present'

                no_of_class = self.verify_welcome_class_from_DB(seo_url)

                if no_of_class[0] >= 1:

                    welcome_class_status = 'Welcome class is present for the program'
                    message = 'Failed'

                else:
                    welcome_class_status = 'Welcome class is not present for the program'
                    message = 'Passed'

            else:
                group_status = 'No groups Available'
                message = 'Passed'

            # pytest.driver.get_screenshot_as_file(os.path.join(os.path.dirname(os.curdir), "report\screenshot", f"{__name__}_{datetime.datetime.now().timestamp()}.png"))
            rows = [[page_type, value, 'Null', 'Null', 'NA',
                     'NA', 'NA', 'NA', group_status, welcome_class_status, message]]
            with open("Report.csv", 'a', newline='\n') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerows(rows)
                
            if 'Failed' in message:
                
                pytest.fail('Next group date is not showing in UI!!!')
        
        # Verifying UI class date is correct or not from DB, if Next group date is present in UI
        elif result[-1] == 'True':

            cls_date = self.verify_UI_class_date_from_DB(result[0], seo_url)

            if cls_date[0] >= 1:

                logging.info('Next group date is showing correct in UI')
                group_status = 'group is present'
                welcome_class_status = 'Welcome class date is matched'
                
            elif cls_date[0] == 0:
                
                logging.info('group date is not matched with UI')
                
                cls_date2 = self.verify_UI_class_date_from_DB_after_converted(result[0], seo_url)
                
                if cls_date2[0] >= 1:
                    
                    logging.info('group date is showing correct in UI after converted')
                    group_status = 'group is present'
                    welcome_class_status = 'Welcome class date is matched after converted'
                    
                else:
                    
                    group_status = 'group is present'
                    welcome_class_status = 'Welcome class date is mismatched after converted'
                    message = 'Failed'
                    logging.info('Incorrect group date is showing in UI after converted')

            else:
                
                group_status = 'No groups Available'
                welcome_class_status = 'Welcome class date is mismatched'
                message = 'Failed'
                logging.info('Incorrect group date is showing in UI')

            # Verifying if Learning Format is 'Blended Learning' or not
            res = self.pg_new_subduct.get_learning_format()
            
            if res == True:

                program_group_details = self.pg_new_subduct.get_program_group_start_date()
                logging.info(
                    f'Program groups details is {program_group_details}')

                if program_group_details is not None:

                    if result[1] == '0' and len(result[2]) >= 3 and len(result[3]) >= 2:
                        message = 'Failed'

                    if program_group_details[1] != result[1] and program_group_details[2] != result[2] and program_group_details[3] != result[3]:
                        message = 'Failed'

                    rows = [[page_type, value, result[0], program_group_details[0],
                            'NA', 'NA', 'NA', 'NA', group_status, welcome_class_status, message]]
                    # logging.info(f'write data is {rows}')
                    with open("Report.csv", 'a', newline='\n') as csvfile:
                        csvwriter = csv.writer(csvfile)
                        csvwriter.writerows(rows)
                        
                    if 'Failed' in message:
                        pytest.fail()
                    
            else:
                
                if result[1] == '0' and len(result[2]) >= 3 and len(result[3]) >= 2:
                    message = 'Failed'

                rows = [[page_type, value, result[0], 'NA',
                        'NA', 'NA', 'NA', 'NA', group_status, welcome_class_status, message]]
                logging.info(f'write data is {rows}')
                with open("Report.csv", 'a', newline='\n') as csvfile:
                    csvwriter = csv.writer(csvfile)
                    csvwriter.writerows(rows)

                if 'Failed' in message:
                    pytest.fail()