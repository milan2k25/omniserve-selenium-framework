import logging
import xml.etree.ElementTree as ET
from interface import Interface, implements
# from logzero import logger
from helper.database import db_helper as db
from datetime import date

def xml_parser_factory(_type,path):
    if _type == 'junit':
        return ParseJunitXml(path)
    else:
        raise TypeError(f"{_type} - report type not supported")
    

class ParseTestResults(Interface):

    def __init__(self,path):
        '''
        Initialize the path of test results
        '''
        pass

    def get_test_details_from_xml(self):
        '''
        parse the test results xml and fetch the required details for the report
        
        | total_tests | passed | failed | skipped | time | timestamp | passed_details | failed_details
        '''
        pass


class ParseJunitXml(implements(ParseTestResults)):

    def __init__(self,path):
        self.path = path

    def get_test_details_from_xml(self):
        global results 
        results = {}

        # create element tree object 
        tree = ET.parse(self.path)

        # get root element 
        root = tree.getroot()

        testsuite_tag = root.find("testsuite")
        results['total_tests'] = int(testsuite_tag.attrib['tests'])
        results['failed'] = int(testsuite_tag.attrib['failures'])
        results['skipped'] = int(testsuite_tag.attrib['skipped'])
        results['passed'] = results['total_tests'] - (results['failed'] + results['skipped'])
        results['timestamp'] = testsuite_tag.attrib['timestamp']

        for _property in testsuite_tag.findall("properties/property"):
            results[_property.attrib['name']] = _property.attrib['value']

        testsuite_tag = root.find("testsuite/testcase")
        results['class_name'] = testsuite_tag.attrib['classname']


    def get_test_details_from_xml_for_product_load(self):
        global results 
        global data
        results = {}
        data = {}

        # create element tree object 
        tree = ET.parse(self.path)

        # get root element 
        root = tree.getroot()
        module_details = {}
        for testcase in root.findall("testsuite/testcase"):
            module_name = self._find_module_name(testcase.findall("properties/property"))
            if testcase.find("failure") != None:
                self._update_module_details(module_details,module_name,'failed')
                continue
            elif testcase.find("skipped") != None:
                self._update_module_details(module_details,module_name,'skipped')
                continue
            
            self._update_module_details(module_details,module_name,'passed')
    
        results['module_details'] = module_details
        print(module_details)
        #results['passed'] = results['total_tests'] - (results['failed'] + results['skipped'])

        #for key in data.keys():
            #passed_value=data[key]['passed']
            #failed_value=data[key]['failed']
            #skipped_value=data[key]['skipped']
            #total_test_case = passed_value + failed_value + skipped_value


    def _find_module_name(self,property_nodes):
        for _property in property_nodes:
            if _property.attrib['name'] == "module":
                return _property.attrib['value']

    def _update_module_details(self,module_dict,module_name,key):
        if module_name not in module_dict.keys():
            module_dict[module_name] = {'passed':0,'failed':0,'skipped':0}
        module_dict[module_name][key] = module_dict[module_name][key] + 1

#daily run data by anonymous is been stored to td_report_details table
def insert_data():
    global insert_queries
    insert_queries = []
    insert_query = f"""INSERT INTO automation_prion.td_report_details(module, sub_module, branch,  test_casecount, pass_count, triggered_by, run_date) 
                    VALUES (
                    "{results['product']}", 
                    "{results['class_name']}",
                    "{results['branch']}",
                    {results['total_tests']}, 
                    {results['passed']},
                    "{results['user_email']}",
                    "{results['timestamp']}");"""
    insert_queries.append(insert_query)
    try:
        db.insert_data(insert_query,'mysql')
        #print(insert_query)
    except Exception as e:
        raise e
    
def insert_product_load_data():
    global insert_queries
    insert_queries = []
    currentdate=date.today()
    for key in results['module_details'].keys():
        passed_value=results['module_details'][key]['passed']
        failed_value=results['module_details'][key]['failed']
        skipped_value=results['module_details'][key]['skipped']
        total_test_case = passed_value + failed_value + skipped_value
        insert_query = f"""INSERT INTO automation_ice9.td_page_load_summary(page_type, total_urls, fail, created_at)
                VALUES(
                '{key}',
                '{total_test_case}',
                '{failed_value}',
                '{currentdate}');"""
        insert_queries.append(insert_query)
        try:
            db.insert_data(insert_query,'mysql')
            print(insert_query)
        except Exception as e:
            raise e

def insert_db_query_leads_production():
    global insert_queries
    insert_queries =[]
    currentdate=date.today()
    list_domains=['Classroom Program','group Master','Degree Program','JG','Master Program','PG New template','Pg Old template','Subgroup','New Subgroup']
    for domains in list_domains:
            insert_query = f"""INSERT INTO automation_prion.td_leads_report_summary(page_type, created_at)
                            VALUES(
                            '{domains}',
                            '{currentdate}');"""
            insert_queries.append(insert_query)
            try:
                    db.insert_data(insert_query,'mysql')
                    #print(insert_query)
            except Exception as e:
                    raise e

def insert_db_query_leads_production_for_certificate_program():
    global insert_queries
    insert_queries =[]
    currentdate=date.today()
    list_domains=['Certificate Program']
    for domains in list_domains:
            insert_query = f"""INSERT INTO automation_prion.td_leads_report_summary(page_type, created_at)
                            VALUES(
                            '{domains}',
                            '{currentdate}');"""
            insert_queries.append(insert_query)
            try:
                    db.insert_data(insert_query,'mysql')
            except Exception as e:
                    raise e