import logging
import os
import sys
import json
import itertools
import pytest
import decimal
import re
import datetime
import random
import time
from dateutil.relativedelta import relativedelta
from operator import itemgetter
from simple_salesforce import Salesforce
from helper.database import db_helper


from selenium.common.exceptions import JavascriptException

sys.path[0] = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)))

import helper.database.db_helper as db
import helper.api_helper as api
import helper.selenium_helper as selenium_helper
from pages.login_page import LoginPage
from helper.aws_helper import CloudWatchInsights, DynamoDB

#To Return the Countries stored in config.json file
def get_countries_from_config():
    return pytest.config["countries"]

#To Return a Dictionary from List of Dictionary based on a key-value pair of that dictionary
def get_dict_from_listdict_by_dictvalue(list_dict, dict_value, dict_key):
    for item in list_dict:
        if item[dict_key] == dict_value:
            return_item = item
            break
    else:
        return_item = None
    return return_item

def convert_decimal_to_str_listdict(list_dict):
    """
    Loop through List of Dictionary and
    Convert the Decimal Object (represented as Decimal('xx.xx')) to 'xx.xx' (String)
    :param: List of Dictionary
    :return: List of Dictionary
    """

    for dict in list_dict:
        for key in dict:
            if isinstance(dict[key], decimal.Decimal):
                dict[key] = str(dict[key])
    return list_dict

def get_floating_number_from_str(str):
    return re.findall("\d+\.\d+", str)[0]

def set_locatori9_cookie():
    date = (datetime.datetime.utcnow() + relativedelta(days=3)).isoformat() + "Z"
    cookie = {'name' : 'locatori9', 'value' : '%7B%22city_id%22%3A%2247%22%2C%22country_id%22%3A%226%22%2C%22region_name%22%3A%22Karnataka%22%2C%22name%22%3A%22Bangalore%22%2C%22status%22%3A%221%22%2C%22longitude%22%3A%2212.976230%22%2C%22latitude%22%3A%2277.603290%22%2C%22location_time_zone%22%3A%22Asia%5C%2FKolkata%22%2C%22isUpdate%22%3Atrue%2C%22callingCode%22%3A%2291%22%2C%22countryCode%22%3A%22IN%22%2C%22countryTimeZone%22%3A%22Asia%5C%2FKolkata%22%2C%22country_name%22%3A%22India%22%2C%22currency_id%22%3A%221%22%2C%22symbol%22%3A%22Rs.%22%2C%22currency_code%22%3A%22INR%22%2C%22world_region%22%3A%22INR%22%2C%22support_number%22%3A%221800-212-7688%22%2C%22clickToCallNumber%22%3A%221800-212-7688%22%2C%22isTollFree%22%3A%221%22%2C%22cdnCountry%22%3A%22IN%22%7D',
                'expires' : date, 'path' : '/', 'domain' : '.example.com',
                'SameSite' : 'Lax'}
    pytest.driver.add_cookie(cookie)

def set_example_viewer_country_cookie(country_code):
    date = (datetime.datetime.utcnow() + relativedelta(days=3)).isoformat() + "Z"
    cookie = {'name' : 'example-Viewer-Country', 'value' : country_code.upper(),
                'expires' : date, 'path' : '/', 'domain' : '.example.com',
                'SameSite' : 'Lax'}
    pytest.driver.add_cookie(cookie)

def check_preview_availability(course_ids: list):
    preview_available = 0
    preview_api_response = {}
    api_url = ""
    try:
        base_api_url = pytest.config['sheldon_url'] + pytest.config['sheldon_api_url'] + pytest.config['api_urls']['getCoursePagePreviewPlaylist']
        for course_id in course_ids:
            if preview_available == 1:
                break
            api_url = base_api_url.replace('{course_id}', str(course_id))
            preview_api_response = (api.get_api_response(api_url, "GET", {}, ""))[1]
            if preview_api_response['status']:
                preview_available = 1 if len(preview_api_response['data']['visible']) > 0 else 0
                
        return preview_available
    except TypeError:
        logging.warning(f"check_preview_availability method, api_url: {api_url}, api_response: {preview_api_response}")
    

def create_dynamic_email(user_type):
    if user_type == "b2c":
        return 'exampleautomation+script' + str(int(time.time())) + '@gmail.com'
    elif user_type == "b2b":
        return 'exampleautomation+script' + str(int(time.time())) + '@yopmail.com'
    else:
        raise KeyError(f"User Type - {user_type} doesn't exist") 

def get_email_hash(email, phone):
    return selenium_helper.execute_script("return btoa('" + email + "," + phone + "')")

def create_dynamic_phone_number():
    return str(random.randint(1111111111,9999999999))

def get_phone_code_number_by_country_code(country_code):
    query = "SELECT callingCode FROM prion.country WHERE code = '" + country_code + "'"
    return "+" + (db.get_test_data(query))[0]['callingCode']

def get_login_credentials_by_user_type(user_type):
    with open("utility/data/login_credentials.json",) as f:
        return json.load(f)[user_type.lower()]

def logout_webengage_user():
    time.sleep(10) #Time for the Webengage Script to Load
    selenium_helper.execute_script("webengage.user.logout();")

def wait_for_webengage_load():
    webengage_loaded = False    
    for counter in range(0,10):
        try:
            if selenium_helper.execute_script("""var result; 
                performance.getEntriesByType("resource").forEach(
                    function(data) { 
                        if(data.initiatorType == "xmlhttprequest" && data.name.match("getUserInfo"))
                            result="Script Loaded";
                    }
                );
                return result;"""):
                webengage_loaded = True
        except JavascriptException:
            webengage_loaded = False
        if webengage_loaded:
            break
        time.sleep(1)
    time.sleep(2)
    return webengage_loaded

class ProductData(object):
    def get_product_details(self, product_id, city_country_id: 0, product_type): 
        country_training_type_mapping= {}
        api_response = {}
        api_url = ""
        try:
            for country_code in pytest.config['country_code_id_mapping']:
                if city_country_id != 0 and (str(pytest.config['country_code_id_mapping'][country_code]) != str(city_country_id)):
                    #If City page and Country of City Page doesn't maches with country_code then continue
                    continue
                api_url = pytest.config['prion_url'] + pytest.config['prion_urls']['frontend_v1_api_url'] 
                api_url = api_url + (pytest.config['api_urls']['getCourseDetailsById'] if product_type == 'course' else pytest.config['api_urls']['getBundleDetailsById'])
                api_url = api_url.replace('{course_id}', str(product_id))
                api_url = api_url.replace('{country_id}', str(pytest.config['country_code_id_mapping'][country_code]))
                api_response = api.get_api_response(api_url,"GET", {},"")
                api_response = api_response[1]
                country_training_type_mapping[country_code] = api_response['data']['sl_product_training_type']
                if city_country_id != 0 and (str(pytest.config['country_code_id_mapping'][country_code]) == str(city_country_id)):
                    #If City page and Country of City Page maches with country_code then break
                    break
            return country_training_type_mapping, api_response['data']['sl_product_category_id'], api_response['data']['sl_product_category']
        except TypeError:
            logging.warning(f"get_product_details method, api_url : {api_url}, api_response: {api_response}")
            return None
            


    def _fetch_valid_urls_course(self):
        query = """SELECT courses.course_id AS product_id, seo.url AS url, courses.displayName AS product,
                    if(courses.agendaUrl IS NOT NULL and courses.agendaUrl != '', 1, 0) AS has_agenda
                    FROM prion.courses INNER JOIN prion.seo 
                        ON seo.linkable_id=courses.course_id 
                    WHERE
                        seo.linkable_type = 'course'
                            AND seo.Url_Type = 'Course'
                            AND seo.status = 1
                            AND seo.noindex = 0
                            AND courses.status = 1
                            AND courses.course_available_for IN ('universal', 'b2c_only')
                            AND courses.hideFromSearch = 0
                            AND courses.is_free = 0
                            AND courses.is_dummy = 0
                    ORDER BY RAND()
                    LIMIT 30;"""
        return db.get_test_data(query)
    
    def _fetch_valid_urls_course_city(self):
        query = """SELECT courses.course_id AS product_id, seo.url AS url, courses.displayName AS product,
                    if(courses.agendaUrl IS NOT NULL and courses.agendaUrl != '', 1, 0) AS has_agenda,
                    replace((json_extract(seo.params, "$.country_id")), '"','') as city_country_id
                    FROM prion.courses INNER JOIN prion.seo 
                        ON seo.linkable_id=courses.course_id 
                    WHERE
                        seo.linkable_type = 'course_city'
                            AND seo.Url_Type = 'City Page'
                            AND seo.status = 1
                            AND seo.noindex = 0
                            AND courses.status = 1
                            AND courses.course_available_for IN ('universal', 'b2c_only')
                            AND courses.hideFromSearch = 0
                            AND courses.is_free = 0
                            AND courses.is_dummy = 0
                    HAVING city_country_id IN (""" + ",".join(str(country_id) for country_id in list(pytest.config['country_code_id_mapping'].values())) + """)
                    ORDER BY RAND()
                    LIMIT 30;"""
        return db.get_test_data(query)

    def _get_course_lvc_enabled_countries(self, course_id, country_codes):
        query = {}
        query['database_name'] = 'prion'
        query['collection_name'] = 'AllWorkshops'
        query['query_type'] = 'find'
        query['query'] = {'course_id':str(course_id[0]), 'training_id':'3', 'startDate': {'$gte':int(time.time())}}
        query['project'] = {'course_id':1, '_id':0}
        response_data = db.get_test_data(query, 'mongo') 
        if len(response_data) > 0:
            for data in response_data:
                logging.info(data)
            return [{'course_id':course_id[0], 'countries':','.join(country_codes)}]
        else:
            return []

    def _get_course_classroom_enabled_countries(self, course_ids, country_codes):
        query = """SELECT workshop.course_id, group_concat(distinct country.code) AS countries
                    FROM prion.workshop LEFT JOIN prion.country
                        ON country.country_id = workshop.country_id
                    WHERE
                        workshop.course_id IN ( """ + ','.join(str(course_id) for course_id in course_ids) + """)
                            AND country.code IN ('""" + "','".join(country_codes) + """')
                            AND workshop.training_id = 1
                            AND workshop.startDate > NOW()
                            AND workshop.startDate < (NOW() + INTERVAL 90 DAY)
                            AND workshop.isSold = 0
                            AND workshop.status = 1
                            AND workshop.workshopStatus = 'active'
                            AND country.status = 1
                    GROUP BY workshop.course_id
                    HAVING COUNT(1) > 0;"""
        return db.get_test_data(query)

    def _get_course_osl_enabled_countries(self, course_ids, country_codes):
        query = """SELECT DISTINCT pricings.course_id, group_concat(distinct country.code) AS countries
                    FROM prion.pricings LEFT JOIN prion.country 
                        ON (country.country_id = pricings.country_id OR country.cluster_id = pricings.cluster_id)
                    WHERE
                        pricings.training_id = 2
                            AND pricings.status = 1
                            AND country.status = 1
                            AND country.code IN ('""" + "','".join(country_codes) + """')
                            AND pricings.course_id IN ( """ + ','.join(str(course_id) for course_id in course_ids) + """)
                            GROUP BY pricings.course_id;"""
        return db.get_test_data(query)

    def _set_course_details_in_final_data(self,final_data,course_data,country_codes,product_enabled_countries,product_type):
        product_enabled_countries = product_enabled_countries[0]["countries"].split(",")
        for country in country_codes:
            key = "course_" + country.lower() + "_" + product_type
            value = {"product_id" : str(course_data["product_id"]) , "url" : course_data["url"], "product" : course_data["product"]}
            
            if country in product_enabled_countries:
                if key in final_data:
                    final_data[key].append(value)
                else:
                    final_data[key] = []
                    final_data[key].append(value)

    def _fetch_valid_urls_bundle(self, country_codes):
        query = """SELECT bundles.bundle_id AS product_id, seo.url AS url, bundles.course_id AS course_id, 
                        group_concat(DISTINCT country.code) AS osl_countries, bundles.display_name AS product,
                        if(bundles.agendaUrl IS NOT NULL and bundles.agendaUrl != '', 1, 0) AS has_agenda 
                    FROM prion.bundles INNER JOIN prion.seo 
                        ON seo.linkable_id = bundles.bundle_id 
					INNER JOIN prion.subscriptionPricing
						ON subscriptionPricing.linkable_id = bundles.bundle_id
					LEFT JOIN prion.country
						ON (country.country_id = subscriptionPricing.country_id OR country.cluster_id = subscriptionPricing.cluster_id)
                    WHERE
                        seo.linkable_type = 'bundle'
                            AND seo.Url_Type = 'Bundle'
                            AND seo.status = 1
                            AND seo.noindex = 0
                            AND bundles.status = 1
                            AND bundles.partialView = 0
                            AND bundles.master_type = 0
                            AND bundles.bundle_available_for IN ('universal', 'b2c_only')
                            AND bundles.hideFromSearch = 0
                            AND subscriptionPricing.status = 1
                            AND country.code IN ('""" + "','".join(country_codes) + """')
					GROUP BY subscriptionPricing.linkable_id
                    ORDER BY RAND()
                    LIMIT 30;"""
        return db.get_test_data(query)
    
    def _fetch_valid_urls_bundle_city(self, country_codes):
        query = """SELECT bundles.bundle_id AS product_id, seo.url AS url, bundles.course_id AS course_id, 
                        group_concat(DISTINCT country.code) AS osl_countries, bundles.display_name AS product,
                        if(bundles.agendaUrl IS NOT NULL and bundles.agendaUrl != '', 1, 0) AS has_agenda,
                        replace((json_extract(seo.params, "$.country_id")), '"','') as city_country_id 
                    FROM prion.bundles INNER JOIN prion.seo 
                        ON seo.linkable_id = bundles.bundle_id 
					INNER JOIN prion.subscriptionPricing
						ON subscriptionPricing.linkable_id = bundles.bundle_id
					LEFT JOIN prion.country
						ON (country.country_id = subscriptionPricing.country_id OR country.cluster_id = subscriptionPricing.cluster_id)
                    WHERE
                        seo.linkable_type = 'bundle_city'
                            AND seo.Url_Type = 'City Page'
                            AND seo.status = 1
                            AND seo.noindex = 0
                            AND bundles.status = 1
                            AND bundles.partialView = 0
                            AND bundles.master_type = 0
                            AND bundles.bundle_available_for IN ('universal', 'b2c_only')
                            AND bundles.hideFromSearch = 0
                            AND subscriptionPricing.status = 1
                            AND country.code IN ('""" + "','".join(country_codes) + """')
                            AND replace((json_extract(seo.params, "$.country_id")), '"','')  IN (""" + ",".join(str(country_id) for country_id in list(pytest.config['country_code_id_mapping'].values())) + """)
                    GROUP BY seo.url
                    ORDER BY RAND()
                    LIMIT 30;"""
        return db.get_test_data(query)

    def _get_bundle_lvc_enabled_countries(self, course_ids, country_codes):
        query = """SELECT country.code
                    FROM prion.country  LEFT OUTER JOIN prion.workshop
                        ON workshop.country_id = country.country_id
                    WHERE
                        workshop.course_id IN ( """ + ','.join(str(course_id) for course_id in course_ids) + """)
                            AND country.code IN ('""" + "','".join(country_codes) + """')
                            AND workshop.training_id = 3
                            AND workshop.startDate > NOW()
                            AND workshop.startDate < (NOW() + INTERVAL 90 DAY)
                            AND workshop.isSold = 0
                            AND workshop.status = 1
                            AND workshop.workshopStatus = 'active'
                            AND country.status = 1
                    GROUP BY 1;"""
        return db.get_test_data(query)

    def _set_bundle_details_in_final_data(self,final_data,bundle_data,country_codes,product_enabled_countries,bundle_type):
        product_enabled_countries = product_enabled_countries[0]["code"] if product_enabled_countries  else []
        osl_enabled_countries = bundle_data["osl_countries"].split(",")
        for country in country_codes:
            key = bundle_type + "_" + country.lower() + "_"
            key = key + "lvc" if country in product_enabled_countries else key + "osl"

            value = {"product_id" : str(bundle_data["product_id"]) , "url" : bundle_data["url"], "product" : bundle_data["product"]}
    
            if (country not in osl_enabled_countries) : 
                #Skipping as Bundle is not valid as OSL / LVC for the particular Country
                continue
            if bundle_type == "bundle_group" and bundle_data["job_guarantee"] == 1 and country.lower() == "in":
                #Skip Adding Job Guarantee group Master for India Country as frontend won't have Enroll Now Button for these
                continue
        
            if key in final_data:
                final_data[key].append(value)
            else:
                final_data[key] = []
                final_data[key].append(value)

    def _fetch_valid_urls_partial_bundle(self, country_codes):
        query = """SELECT bundles.bundle_id AS product_id, seo.url AS url, bundles.course_id AS course_id, 
                        group_concat(DISTINCT country.code) AS osl_countries, bundles.display_name AS product 
                    FROM prion.bundles INNER JOIN prion.seo 
                        ON seo.linkable_id = bundles.bundle_id 
					INNER JOIN prion.subscriptionPricing
						ON subscriptionPricing.linkable_id = bundles.bundle_id
					LEFT JOIN prion.country
						ON (country.country_id = subscriptionPricing.country_id OR country.cluster_id = subscriptionPricing.cluster_id)
                    WHERE
                        seo.linkable_type = 'bundle'
                            AND seo.Url_Type = 'Bundle'
                            AND seo.status = 1
                            AND seo.noindex = 0
                            AND bundles.status = 1
                            AND bundles.partialView = 1
                            AND bundles.master_type = 0
                           -- AND bundles.bundle_available_for IN ('universal', 'b2c_only')
                            -- AND bundles.hideFromSearch = 0
                            AND subscriptionPricing.status = 1
                            AND country.code IN ('IN', 'US', 'GB', 'DE', 'AU', 'SG')
					GROUP BY subscriptionPricing.linkable_id
                    ORDER BY RAND()
                    LIMIT 30;"""
        return db.get_test_data(query)

    def _fetch_valid_urls_group_bundle(self, country_codes):
        query = """SELECT bundles.bundle_id AS product_id, seo.url AS url, bundles.course_id AS course_id, 
                        group_concat(DISTINCT country.code) AS osl_countries, bundles.job_guarantee, bundles.display_name AS product,
                        if(bundles.agendaUrl IS NOT NULL and bundles.agendaUrl != '', 1, 0) AS has_agenda 
                    FROM prion.bundles INNER JOIN prion.seo 
                        ON seo.linkable_id = bundles.bundle_id 
					INNER JOIN prion.subscriptionPricing
						ON subscriptionPricing.linkable_id = bundles.bundle_id
					LEFT JOIN prion.country
						ON (country.country_id = subscriptionPricing.country_id OR country.cluster_id = subscriptionPricing.cluster_id)
                    WHERE
                        seo.linkable_type = 'bundle'
                            AND seo.Url_Type = 'Bundle'
                            AND seo.status = 1
                            AND seo.noindex = 0
                            AND bundles.status = 1
                            AND bundles.partialView = 0
                            AND bundles.master_type = 2
                            AND bundles.bundle_available_for IN ('universal', 'b2c_only')
                            AND bundles.hideFromSearch = 0
                            AND subscriptionPricing.status = 1
                            AND country.code IN ('""" + "','".join(country_codes) + """')
					GROUP BY subscriptionPricing.linkable_id
                    ORDER BY RAND()
                    LIMIT 30;"""
        return db.get_test_data(query)
    
    def _fetch_valid_urls_group_bundle_city(self, country_codes):
        query = """SELECT bundles.bundle_id AS product_id, seo.url AS url, bundles.course_id AS course_id, 
                        group_concat(DISTINCT country.code) AS osl_countries, bundles.job_guarantee, bundles.display_name AS product,
                        if(bundles.agendaUrl IS NOT NULL and bundles.agendaUrl != '', 1, 0) AS has_agenda,
                        replace((json_extract(seo.params, "$.country_id")), '"','') as city_country_id  
                    FROM prion.bundles INNER JOIN prion.seo 
                        ON seo.linkable_id = bundles.bundle_id 
					INNER JOIN prion.subscriptionPricing
						ON subscriptionPricing.linkable_id = bundles.bundle_id
					LEFT JOIN prion.country
						ON (country.country_id = subscriptionPricing.country_id OR country.cluster_id = subscriptionPricing.cluster_id)
                    WHERE
                        seo.linkable_type = 'bundle_city'
                            AND seo.Url_Type = 'City Page'
                            AND seo.status = 1
                            AND seo.noindex = 0
                            AND bundles.status = 1
                            AND bundles.partialView = 0
                            AND bundles.master_type = 2
                            AND bundles.bundle_available_for IN ('universal', 'b2c_only')
                            AND bundles.hideFromSearch = 0
                            AND subscriptionPricing.status = 1
                            AND country.code IN ('""" + "','".join(country_codes) + """')
                            AND replace((json_extract(seo.params, "$.country_id")), '"','')  IN (""" + ",".join(str(country_id) for country_id in list(pytest.config['country_code_id_mapping'].values())) + """)
                    GROUP BY seo.url
                    ORDER BY RAND()
                    LIMIT 30;"""
        return db.get_test_data(query)

    def _fetch_valid_urls_university_bundle(self, country_codes):
        query = """SELECT bundles.bundle_id AS product_id, seo.url AS url, bundles.course_id AS course_id, 
                        group_concat(DISTINCT country.code) AS osl_countries, bundles.job_guarantee, bundles.display_name AS product,
                        if(bundles.agendaUrl IS NOT NULL and bundles.agendaUrl != '', 1, 0) AS has_agenda 
                    FROM prion.bundles INNER JOIN prion.seo 
                        ON seo.linkable_id = bundles.bundle_id 
					INNER JOIN prion.subscriptionPricing
						ON subscriptionPricing.linkable_id = bundles.bundle_id
					LEFT JOIN prion.country
						ON (country.country_id = subscriptionPricing.country_id OR country.cluster_id = subscriptionPricing.cluster_id)
                    WHERE
                        seo.linkable_type = 'bundle'
                            AND seo.Url_Type = 'Bundle'
                            AND seo.status = 1
                            AND seo.noindex = 0
                            AND bundles.status = 1
                            AND bundles.partialView = 0
                            AND bundles.master_type = 1
                            AND bundles.bundle_available_for IN ('universal', 'b2c_only')
                            AND bundles.hideFromSearch = 0
                            AND subscriptionPricing.status = 1
                            AND country.code IN ('""" + "','".join(country_codes) + """')
					GROUP BY subscriptionPricing.linkable_id
                    ORDER BY RAND()
                    LIMIT 30;"""
        return db.get_test_data(query)

    def _fetch_valid_urls_university_bundle_city(self, country_codes):
        query = """SELECT bundles.bundle_id AS product_id, seo.url AS url, bundles.course_id AS course_id, 
                        group_concat(DISTINCT country.code) AS osl_countries, bundles.job_guarantee, bundles.display_name AS product,
                        if(bundles.agendaUrl IS NOT NULL and bundles.agendaUrl != '', 1, 0) AS has_agenda,
                        replace((json_extract(seo.params, "$.country_id")), '"','') as city_country_id  
                    FROM prion.bundles INNER JOIN prion.seo 
                        ON seo.linkable_id = bundles.bundle_id 
					INNER JOIN prion.subscriptionPricing
						ON subscriptionPricing.linkable_id = bundles.bundle_id
					LEFT JOIN prion.country
						ON (country.country_id = subscriptionPricing.country_id OR country.cluster_id = subscriptionPricing.cluster_id)
                    WHERE
                        seo.linkable_type = 'bundle_city'
                            AND seo.Url_Type = 'City Page'
                            AND seo.status = 1
                            AND seo.noindex = 0
                            AND bundles.status = 1
                            AND bundles.partialView = 0
                            AND bundles.master_type = 1
                            AND bundles.bundle_available_for IN ('universal', 'b2c_only')
                            AND bundles.hideFromSearch = 0
                            AND subscriptionPricing.status = 1
                            AND country.code IN ('""" + "','".join(country_codes) + """')
                            AND replace((json_extract(seo.params, "$.country_id")), '"','')  IN (""" + ",".join(str(country_id) for country_id in list(pytest.config['country_code_id_mapping'].values())) + """)
                    GROUP BY seo.url
                    ORDER BY RAND()
                    LIMIT 30;"""
        return db.get_test_data(query)

    def _course(self, final_data):
        country_codes =  get_countries_from_config()

        courses_data = self._fetch_valid_urls_course()
        
        for course_data in courses_data:
            lvc_enabled_countries = self._get_course_lvc_enabled_countries([course_data["product_id"]], country_codes)
            classroom_enabled_countries = self._get_course_classroom_enabled_countries([course_data["product_id"]], country_codes)
            osl_enabled_countries = self._get_course_osl_enabled_countries([course_data["product_id"]], country_codes)
           
            if lvc_enabled_countries:
                self._set_course_details_in_final_data(final_data,course_data,country_codes,lvc_enabled_countries,"lvc")
            #(not course_data['product_id'] in [766, 1391,1425]) Exception added for Temporary Purpose 
            #as currently the Training Type is disabled in frontend for these SaFe Related Classroom Programs
            if classroom_enabled_countries and (not course_data["product_id"] in ["766", "1391","1425"]):
                self._set_course_details_in_final_data(final_data,course_data,country_codes,classroom_enabled_countries,"classroom")
            if osl_enabled_countries:
                self._set_course_details_in_final_data(final_data,course_data,country_codes,osl_enabled_countries,"osl")

    def _bundle(self, final_data):
        country_codes = country_codes =  get_countries_from_config()

        bundles_data = self._fetch_valid_urls_bundle(country_codes)
        for bundle_data in bundles_data:
            lvc_enabled_countries = self._get_bundle_lvc_enabled_countries([bundle_data["course_id"]], country_codes)
          
            self._set_bundle_details_in_final_data(final_data,bundle_data,country_codes,lvc_enabled_countries, "bundle")
        
        partial_bundles_data = self._fetch_valid_urls_partial_bundle(country_codes)
        for partial_bundle_data in partial_bundles_data:
            self._set_bundle_details_in_final_data(final_data,partial_bundle_data,country_codes,[], "bundle_partial")

        group_bundles_data = self._fetch_valid_urls_group_bundle(country_codes)
        for group_bundle_data in group_bundles_data:
            lvc_enabled_countries = self._get_bundle_lvc_enabled_countries([group_bundle_data["course_id"]], country_codes)
          
            self._set_bundle_details_in_final_data(final_data,group_bundle_data,country_codes,lvc_enabled_countries, "bundle_group")

        university_bundles_data = self._fetch_valid_urls_university_bundle(country_codes)
        for university_bundle_data in university_bundles_data:
            lvc_enabled_countries = self._get_bundle_lvc_enabled_countries([university_bundle_data["course_id"]], country_codes)
          
            self._set_bundle_details_in_final_data(final_data,university_bundle_data,country_codes,lvc_enabled_countries, "bundle_university")

    def _lvc_pass(self, final_data):
        #We don't use LVC PASS any more hence skipping this method
        pass

    def _category(self, final_data):
        #Need to add data to fetch corresponding category data and add in json
        pass

    def _master_of_masters(self, final_data):
        country_codes =  get_countries_from_config()

        for country in country_codes:
            key = "mom_tech_" + country.lower() + "_"
            value = {"product_id" : "126" , "url" : "/tech-master-of-masters-program", "product" : "Tech Master of Master's Program"}
            final_data[key] = []
            final_data[key].append(value)

            value = {"product_id" : "259" , "url" : "/management-master-of-masters-program", "product" : "Management Master of Master's Program"}
            final_data[key] = []
            final_data[key].append(value)

            key = "mom_dual_" + country.lower() + "_"
            value = {"product_id" : "155" , "url" : "/data-science-and-artificial-intelligence-masters-program", "product" : "Data Science And Artificial Intelligence"}
            final_data[key] = []
            final_data[key].append(value)

    def get_product_types(self):
        query = "SELECT product_type_name FROM prion.productTypes;"
        return db.get_test_data(query)

    def get_lvc_classroom_courses(self, country_codes):
        query = {}
        query['database_name'] = 'prion'
        query['collection_name'] = 'AllWorkshops'
        query['query_type'] = 'aggregate'
        query['query'] = [{'$match': {'training_id': {'$in': ['3','1']}, 'startDate': {'$gte':int(time.time())}}},{'$group':{ '_id':'$training_id', 'course_id':{'$addToSet':{'$concat' :['$course_id']}}}}]
        response_data = db.get_test_data(query, 'mongo')
        return_data=[]
        if len(response_data) > 0:
            for data in response_data:
                for country in country_codes:
                    product = 'course_' + country + '_lvc' if data['_id'] == 3 else '_classroom'
                    return_data.append({'product':product, 'product_id':','.join(course_id for course_id in data['course_id'])})
            return return_data
        else:
            return []
    
    def get_bundlesdata_by_courses(self, course_ids):
        query = """SELECT DISTINCT
                        courseMapping.linkable_id AS product_id, seo.url AS url 
                    FROM
                        prion.courseMapping
                            INNER JOIN
                        prion.bundles ON bundles.bundle_id = courseMapping.linkable_id
                            INNER JOIN
                        prion.seo ON seo.linkable_id = bundles.bundle_id
                    WHERE
                        courseMapping.status = 1
                            AND courseMapping.product_type = 'course'
                            AND bundles.status = 1
                            AND seo.status = 1
                            AND seo.linkable_type = 'bundle'
                            AND bundles.hideFromSearch = 0
                            AND bundles.master_type = 0
                            AND courseMapping.product_id IN (""" + ','.join(course_ids.split(",")) + """);"""

        return db.get_test_data(query)
    
    def get_coursesdata_by_courseid(self, course_ids):
        query = """SELECT courses.course_id AS product_id, seo.url AS url 
                    FROM prion.courses INNER JOIN prion.seo 
                        ON seo.linkable_id=courses.course_id 
                    WHERE
                        seo.linkable_type = 'course'
                            AND seo.Url_Type = 'Course'
                            AND seo.status = 1
                            AND seo.noindex = 0
                            AND courses.status = 1
                            AND courses.course_available_for IN ('universal', 'b2c_only')
                            AND courses.hideFromSearch = 0
                            AND courses.is_free = 0
                            AND courses.is_dummy = 0
                            AND courses.course_id IN (""" + ','.join(course_ids.split(",")) + """)
                    ORDER BY RAND()
                    LIMIT 1;"""

        return db.get_test_data(query)
    
    def _refetch_product_data(self, final_data):
        country_codes = get_countries_from_config()
        functions = {
            "course": self.get_coursesdata_by_courseid,
            "bundle": self.get_bundlesdata_by_courses
        }
        lvc_classroom_courses = self.get_lvc_classroom_courses(country_codes)

        key_product_type = ["course_lvc", "course_classroom", "bundle_lvc"]
        for country, product_type in itertools.product(country_codes, key_product_type):
            key = product_type.split("_")[0] + "_" + country.lower() + "_" + product_type.split("_")[1]
            if not key in final_data.keys():
                product = get_dict_from_listdict_by_dictvalue(lvc_classroom_courses, key if product_type.split("_")[0] == "course" else key.replace("bundle", "course"), "product")
                func = functions[product_type.split("_")[0]]
                product_data = func(product["product_id"]) if product else None
                if product_data:
                    product_data = product_data[0]
                    value = {"product_id" : str(product_data["product_id"]) , "url" : product_data["url"]}
                    final_data[key] = []
                    final_data[key].append(value)

    def add_random_country_trainingtype_product_details_to_json(self):
        functions = {
            'course' : self._course,
            'bundle': self._bundle,
            'lvc_pass' : self._lvc_pass,
            'category' : self._category,
            'master_of_masters' : self._master_of_masters
        }

        product_types = self.get_product_types()

        final_data = {}
        for product_type in product_types:
            func = functions[product_type["product_type_name"]]
            func(final_data)

        #Re-check once again if URLs are available or not. If available will add 1 random URL against the ProductType, Country & TrainingType Combination
        self._refetch_product_data(final_data)

        with open('utility/data/country_trainingtype_productdata.json', 'w') as outfile:
            outfile.truncate(0)
            json.dump(final_data, outfile, indent=4)

    def _course_program_data(self, final_data, page_type):
        functions = {
            'course': self._fetch_valid_urls_course, 
            'course_city_page': self._fetch_valid_urls_course_city
        }
        func = functions[page_type]
        courses_data = func()
        for course_data in courses_data:
            city_country_id = course_data['city_country_id'].decode("utf-8") if 'city_country_id' in course_data else 0
            course_details_api_response = self.get_product_details(course_data['product_id'], city_country_id, 'course')
            if not course_details_api_response:
                logging.warning(f"Course Data: Skipped, data not available in any database/collection for all countries for product id: {course_data['product_id']}")
                continue
            json_data = {"Entry_Page": pytest.config['sheldon_url'][:-1] + course_data['url'], 
                            "sl_product_id": course_data['product_id'], 
                            "sl_product_name": course_data['product'],
                            "syllabus_available" : course_data['has_agenda'],
                            "preview_available" : check_preview_availability(list(str(course_data['product_id']).split(","))),
                            "country_training_type_mapping": course_details_api_response[0],
                            "sl_product_category_id": course_details_api_response[1],
                            "sl_product_category": course_details_api_response[2],
                            "city_country": city_country_id}
            final_data[page_type].append(json_data)
    
    def _master_program_data(self, final_data, page_type):
        functions = {
            'classic_masters_program': self._fetch_valid_urls_bundle, 
            'classic_masters_city_page': self._fetch_valid_urls_bundle_city, 
            'university_masters_program': self._fetch_valid_urls_university_bundle, 
            'university_masters_city_page': self._fetch_valid_urls_university_bundle_city, 
            'group_masters_program': self._fetch_valid_urls_group_bundle, 
            'group_masters_city_page': self._fetch_valid_urls_group_bundle_city,
            'frs_article_page':self._fetch_valid_urls_group_bundle_city
        }
        func = functions[page_type]
        bundles_data = func(get_countries_from_config())
        for bundle_data in bundles_data:
            city_country_id = bundle_data['city_country_id'].decode("utf-8") if 'city_country_id' in bundle_data else 0
            bundle_details_api_response = self.get_product_details(bundle_data['product_id'], city_country_id, 'bundle')
            if not bundle_details_api_response:
                logging.warning(f"Bundle Data: Skipped, data not available in any database/collection for all countries for product id: {bundle_data['product_id']}")
                continue
            job_guarantee = 0
            if "job_guarantee" in bundle_data and bundle_data["job_guarantee"]:
                 job_guarantee = 1
                 if city_country_id != 0 and str(city_country_id) != str(pytest.config['country_code_id_mapping']["IN"]):
                    job_guarantee = 0

            json_data = {"Entry_Page": pytest.config['sheldon_url'][:-1] + bundle_data['url'], 
                            "sl_product_id": bundle_data['product_id'], 
                            "sl_product_name": bundle_data['product'],
                            "syllabus_available" : bundle_data['has_agenda'],
                            "preview_available" : check_preview_availability(list(bundle_data['course_id'].split(","))),
                            "country_training_type_mapping": bundle_details_api_response[0],
                            "sl_product_category_id": bundle_details_api_response[1],
                            "sl_product_category": bundle_details_api_response[2],
                            "city_country": city_country_id,
                            "is_job_guarantee": job_guarantee}
            final_data[page_type].append(json_data)

    def add_random_product_details_by_product_type_to_json(self):
        functions = {
            'course': self._course_program_data, 
            'course_city_page': self._course_program_data, 
            'classic_masters_program': self._master_program_data, 
            'classic_masters_city_page': self._master_program_data, 
            'university_masters_program': self._master_program_data, 
            'university_masters_city_page': self._master_program_data, 
            'group_masters_program': self._master_program_data, 
            'group_masters_city_page': self._master_program_data,
            'frs_article_page':self._master_program_data
        }
        pages_types = pytest.config["page_types"]

        final_data = {}
        for page_type in pages_types:
            func = functions[page_type]
            final_data[page_type] = []
            func(final_data, page_type)
        
        with open('utility/data/lead_productdata.json', 'w') as outfile:
            outfile.truncate(0)
            json.dump(final_data, outfile, indent=4)
    
    def get_url_data(self):
        query = f"""SELECT 
                s.url AS 'example_url',
                CONCAT('http://',
                        u.university_domain,
                        ':{pytest.config['port']}',
                        s.url) AS 'university_url'
            FROM
                prion.seo s
                    LEFT JOIN
                prion.university_mapping um ON um.linkable_id = s.linkable_id
                    LEFT JOIN
                prion.university u ON u.university_id = um.university_id
            WHERE
                s.controller = 'university-domain'
                    AND s.linkable_id IS NOT NULL
            ORDER BY RAND()
            LIMIT 1;"""
        response = db.get_test_data(query)
        response = response[0]
        json_data = {"university_url": response['university_url'],
                      "example_url":response['example_url']}

        with open('utility/data/mql_lead_data.json', 'w') as outfile:
            outfile.truncate(0)
            json.dump(json_data, outfile)

    def get_status_of_url(self,url):
        query = """SELECT status from prion.seo_geetha WHERE
                    url in('"""+url+"""');"""
        return db.get_test_data(query)
    
    def get_migrated_data_of_url(self,url):
        query = """SELECT redirect_url,status_code from prion.seo WHERE
                    url in('"""+url+"""');"""
        return db.get_test_data(query)

    def get_bundle_data(self):
        query = """SELECT distinct primary_label_id, bundle_id AS product_id, display_name 
                        FROM prion.bundles AS b 
                        INNER JOIN prion.seo AS s 
                            ON s.linkable_id=b.bundle_id 
                        WHERE s.status=1 AND s.controller="bundle" 
                        AND b.bundle_available_for IN ("universal", "b2c_only") 
                        -- AND (b.primary_label_id IN (1) OR b.label_id IN (1)) 
                        AND b.status=1;"""
        return db.get_test_data(query)

    def get_course_data(self):
        query = """SELECT distinct primary_label_id, course_id AS product_id, displayName AS display_name 
                        FROM prion.courses AS c 
                        INNER JOIN prion.seo AS s 
                            ON s.linkable_id=c.course_id 
                        WHERE s.status=1 AND s.controller="course" 
                        AND c.course_available_for IN ("universal", "b2c_only") 
                        -- AND (b.primary_label_id IN (1) OR b.label_id IN (1)) 
                        AND c.status=1;"""
        return db.get_test_data(query)


    def get_product(self):

        #pro_data = self.get_bundle_data()
        pro_data = self.get_course_data()
        final_data = {}
        for key in pro_data:
            id = key['primary_label_id']
            if id in final_data:
                self._addd(key,final_data)
            else:
                final_data[key['primary_label_id']] = {}
                self._addd(key,final_data)

        with open('utility/data/productdata.json', 'w') as outfile:
            outfile.truncate(0)
            json.dump(final_data, outfile, indent=4)
        
    def _addd(self,key,final_data):
        data= {}
        data = final_data[key['primary_label_id']]
        data[key['product_id']] = key['display_name']
        final_data[key['primary_label_id']] = data
        return final_data

    def _faqstatus(self,country_id,course_id,faq_id):
        query = """SELECT cf.course_faq_id AS faqid, cm.status AS cmstatus, cf.status AS cfstatus
            FROM prion.courseFaq AS cf
            INNER JOIN prion.course_resource_mapping AS cm 
                ON cm.faq_id = cf.course_faq_id
            INNER JOIN prion.course_city_lookup AS cl 
                ON cl.id = cm.lookup_id
            WHERE cf.type = 4 
                AND (cl.country_id='"""+ country_id +"""' AND cl.cluster_id=0 AND cl.city_id=0) 
                AND cl.course_id= '"""+ course_id +"""'
                AND cm.faq_id= '""" + faq_id + """'
                AND cf.training_id=0 
                AND cl.linkable_type="freemium_course"
                AND cl.status = 1;"""
        return db.get_test_data(query)

    def get_freemium_course_basics_data(self,course_id):
        query="""SELECT c.name as course_name,s.tag as tags, c.label_id as label_id, l.name as label_name, c.primary_eLearning_id as elearning_id, c.totalDuration as total_hours 
            FROM prion.courses AS c
            INNER JOIN prion.searchTags as s
            on c.course_id=s.linkable_id
            INNER JOIN prion.labels as l
            on c.label_id=l.label_id
            WHERE s.status=1
            AND s.linkable_type='course'
            AND c.course_id='"""+course_id+"""';"""
        return db.get_test_data(query)

    def get_course_advisors_data(self,course_id):
        query="""SELECT concat(s.section_id,' - ', p.name ) as course_advisors
            FROM prion.sectionMapping as s INNER JOIN prion.productSectionData as p ON s.section_id=p.id
            WHERE s.linkable_id='"""+course_id+"""' AND s.linkable_type='course' 
            AND s.status=1 AND p.sectionTitle='Course Advisor';"""
        return db.get_test_data(query)
    
    def get_best_suited_for_data(self,course_id):
        query="""SELECT p.name as best_suited_value,p.status as product_status,m.status as mapping_status 
            FROM prion.freemium_section_mapping as m
            INNER JOIN prion.freemium_product_section as p
            ON m.product_section_id=p.id WHERE p.section_type='best_suited' AND m.linkable_id='"""+course_id+"""';"""
        return db.get_test_data(query)
    
    def get_id_of_best_suited_data(self,course_id,best_suited_data):
        query="""SELECT m.product_section_id as id_of_the_data from prion.freemium_section_mapping as m 
            inner join prion.freemium_product_section as p
            on m.product_section_id=p.id where p.section_type='best_suited' 
            and m.linkable_id='"""+course_id+"""' and p.name='"""+best_suited_data+"""'
            and p.status=1 and m.status=1;"""
        return db.get_test_data(query)
    
    def get_status_of_best_suited_data(self,course_id,id_of_the_data):
        query="""SELECT m.product_section_id as Id,p.status as product_status,m.status as mapping_status
            FROM prion.freemium_section_mapping as m
            INNER JOIN prion.freemium_product_section as p
            ON m.product_section_id=p.id WHERE p.section_type='best_suited' 
            AND m.linkable_id='"""+course_id+"""' AND m.product_section_id='"""+id_of_the_data+"""';"""
        return db.get_test_data(query)

    def get_job_guarantee_enabled_countries(self, sl_product_id):
        query = """SELECT DISTINCT config 
                FROM prion.productSectionData psd 
                    INNER JOIN prion.sectionMapping sm ON sm.section_id=psd.id 
                    INNER JOIN prion.bundles b ON b.bundle_id=sm.linkable_id
                WHERE b.bundle_id=""" + str(sl_product_id) + """ AND b.job_guarantee = 1 AND psd.sectionType='job_guarantee' AND psd.config IS NOT NULL 
                    AND b.status=1 AND psd.status=1 AND sm.status=1;"""
        jg_config_data = db.get_test_data(query)
        country_data = []
        for data in jg_config_data:
            country_data.append(pytest.mappings['country_id_code_mapping'][str(json.loads(data['config'])['country_id'])])
        return country_data


class OrderData(object):
    def get_ssvc_cart_data(self, token):
        query = """SELECT status, time, token, countryCode, 
                        emailId, orderId, paymentGateway, paymentGatewayTransactionId, contactNumber
                    FROM ssvc.cart 
                    WHERE token='""" + token + """';"""
        return convert_decimal_to_str_listdict(db.get_test_data(query))

    def get_ssvc_transaction_userdata_data(self, token):
        query = """SELECT token, reason, time, gateway 
                    FROM ssvc.transaction_userdata 
                    WHERE token='""" + token + """' 
                    ORDER BY id DESC 
                    LIMIT 1;"""
        return convert_decimal_to_str_listdict(db.get_test_data(query))
    
    def get_melv1n_orders_data(self, token):
        query = """SELECT paymentStatus, order_id, orderNumber, date, user_id, userEmail, authToken, 
                        paymentGateway, currency_id, contactNumber, serviceTax, netTotal, countryCode 
                    FROM melv1n.orders 
                    WHERE authToken='""" + token + """';"""
        return convert_decimal_to_str_listdict(db.get_test_data(query))
    
    def get_melv1n_orderdetails_data(self, order_id):
        query = """SELECT * 
                    FROM melv1n.orderDetails 
                    WHERE order_id=""" + str(order_id) + """;"""
        return convert_decimal_to_str_listdict(db.get_test_data(query))

    def get_melv1n_orderstax_data(self, order_id):
        query = """SELECT * 
                    FROM melv1n.ordersTax 
                    WHERE order_id=""" + str(order_id) + """;"""
        return convert_decimal_to_str_listdict(db.get_test_data(query))

    def get_melv1n_paymentreconciliations_data(self, token):
        query = """SELECT customerEmail, orderNumber, currency, amount 
                    FROM melv1n.paymentReconciliations 
                    WHERE token='""" + token + """';"""
        return convert_decimal_to_str_listdict(db.get_test_data(query))

    def get_paperclip_assignmentrequest_data(self, order_number):
        query = """SELECT * 
                    FROM paperclip_atlas.assignment_request 
                    WHERE orderNumber='""" + order_number + """';"""
        return convert_decimal_to_str_listdict(db.get_test_data(query))

class LeadUtility(object):

    def __init__(self,form_name):
        self.form_name = form_name
        self.page_name = ""
        self.previous_email = ""
        self.previous_phone = ""
        self.url_data = {}
        self.previous_urls_list = []
        self.previous_url_data = {}

    def before_lead_submission(self, page_name):
        if self.page_name != page_name:
            self.page_name = page_name
            self.previous_email = ""
            self.previous_phone = ""
            self.previous_urls_list = []
            self.previous_url_data = {}
    
    def get_form_eligible_urls_list(self, lead_product_data):
        final_product_data = []
        if (self.form_name == pytest.mappings['lead_form_name']['REQUEST_MORE_INFORMATION']
        or self.form_name == pytest.mappings['lead_form_name']['REQUEST_A_CALLBACK']
        or self.form_name == pytest.mappings['lead_form_name']['SCHEDULE_A_CALL']
        or self.form_name == pytest.mappings['lead_form_name']['APPLY_NOW']
            or self.form_name == pytest.mappings['lead_form_name']['COURSE_PREVIEW']):
            for product_data in lead_product_data:
                if product_data['preview_available'] == 1:
                    final_product_data.append(product_data)
        elif self.form_name == pytest.mappings['lead_form_name']['DOWNLOAD_SYLLABUS']:
            for product_data in lead_product_data:
                if product_data['preview_available'] == 1 and product_data['syllabus_available'] == 1:
                    final_product_data.append(product_data)
        elif self.form_name == pytest.mappings['lead_form_name']['JOB_GUARANTEE_BROCHURE']:
            for product_data in lead_product_data:
                if product_data['is_job_guarantee'] == 1:
                    final_product_data.append(product_data)
        elif self.form_name == pytest.mappings['lead_form_name']['FRS_BANNER_B2C']:
            for frs_data in lead_product_data:
                if not frs_data['is_b2b']:
                    final_product_data.append(frs_data)
        elif self.form_name == pytest.mappings['lead_form_name']['FRS_BANNER_B2B']:
            for frs_data in lead_product_data:
                if frs_data['is_b2b']:
                    final_product_data.append(frs_data)
        elif self.form_name == pytest.mappings['lead_form_name']['FRS_BANNER_MQL']:
            for frs_data in lead_product_data:
                if frs_data['mql_banner_countries']:
                    final_product_data.append(frs_data)
        else:
            final_product_data = lead_product_data
        return final_product_data

    def _get_random_url(self, lead_product_data, test_type):
        if self.previous_url_data:
            self.url_data = self.previous_url_data.copy()
        else:
            self.url_data = random.choice(self.get_form_eligible_urls_list(lead_product_data[self.page_name]))
            self.previous_url_data = self.url_data.copy()
    
    def _get_random_url_with_previous(self, lead_product_data, test_type):
        if (test_type == pytest.mappings['lead_test_type']['SUBMIT_LEAD'] or test_type == pytest.mappings['lead_test_type']['LOGIN_AUH_PREFILL_SUBMIT_LEAD'] or
            test_type == pytest.mappings['lead_test_type']['WE_AUH_PREFILL_SUBMIT_LEAD'] or test_type == pytest.mappings['lead_test_type']['AUH_PREFILL_SUBMIT_LEAD']
            or test_type == pytest.mappings['lead_test_type']['LOGIN_PREFILL_SUBMIT_LEAD']):
            if self.previous_urls_list:
                url = random.choice(self.previous_urls_list)
                self.url_data = self.previous_url_data[url].copy()
            else:
                final_product_data = self.get_form_eligible_urls_list(lead_product_data[self.page_name])
                random_url_index = random.randint(0, len(final_product_data)-1)
                self.url_data = final_product_data[random_url_index].copy()
                self.previous_urls_list.append(final_product_data[random_url_index]['Entry_Page'])
                self.previous_url_data[final_product_data[random_url_index]['Entry_Page']] = final_product_data[random_url_index].copy()
        else:
            temp_url_data = {}
            for previous_url_check_counter in range (0,20):
                final_product_data = self.get_form_eligible_urls_list(lead_product_data[self.page_name])
                random_url_index = random.randint(0, len(final_product_data)-1)
                if final_product_data[random_url_index]['Entry_Page'] not in self.previous_urls_list:
                    self.url_data = final_product_data[random_url_index].copy()
                    temp_url_data = final_product_data[random_url_index].copy()
                    break
            self.previous_urls_list.append(temp_url_data['Entry_Page'])
            self.previous_url_data[temp_url_data['Entry_Page']] = temp_url_data

    def fetch_random_url(self, test_type):
        lead_data = []
        with open("utility/data/lead_productdata.json",) as f:
            lead_data.append(json.load(f))
        
        with open("utility/data/frs_data.json",) as f:
            lead_data.append(json.load(f))
        
       

        functions = {
            pytest.mappings['lead_form_name']['REQUEST_MORE_INFORMATION'] : self._get_random_url,
            pytest.mappings['lead_form_name']['TALK_WITH_COUNSELOR'] : self._get_random_url,
            pytest.mappings['lead_form_name']['SCHEDULE_A_CALL'] : self._get_random_url,
            pytest.mappings['lead_form_name']['APPLY_NOW'] : self._get_random_url_with_previous,
            pytest.mappings['lead_form_name']['COURSE_PREVIEW'] : self._get_random_url_with_previous,
            pytest.mappings['lead_form_name']['DOWNLOAD_SYLLABUS'] : self._get_random_url_with_previous,
            pytest.mappings['lead_form_name']['JOB_GUARANTEE_BROCHURE'] : self._get_random_url_with_previous,
            pytest.mappings['lead_form_name']['MQL_DOWNLOAD_BROCHURE'] : self._get_random_url,
            pytest.mappings['lead_form_name']['MQL_REQUEST_A_CALLBACK'] : self._get_random_url,
            pytest.mappings['lead_form_name']['REQUEST_A_CALLBACK'] : self._get_random_url_with_previous,
            pytest.mappings['lead_form_name']['FRS_BANNER_B2C'] : self._get_random_url,
            pytest.mappings['lead_form_name']['FRS_BANNER_B2B'] : self._get_random_url,
            pytest.mappings['lead_form_name']['FRS_BANNER_MQL'] : self._get_random_url,

        }
        func = functions[self.form_name]
        if "frs" in self.form_name.lower():
            func(lead_data[1], test_type)
        else: 
            func(lead_data[0], test_type)


            
    def lead_settings(self, test_data):
        sl_user_email = create_dynamic_email(test_data['queryType'])
        sl_user_phone = get_phone_code_number_by_country_code(test_data['countryCode']) + "-" + create_dynamic_phone_number()

        login_credentials = random.choice(get_login_credentials_by_user_type(test_data['queryType']))

        if test_data['test_type'] == pytest.mappings['lead_test_type']['SUBMIT_LEAD'] or test_data['test_type'] == pytest.mappings['lead_test_type']['MQL_SUBMIT_LEAD']:
            pytest.driver.delete_all_cookies()
            logout_webengage_user()
            test_data['sl_user_email'] = sl_user_email
            test_data['sl_user_phone'] = sl_user_phone
            test_data["prefilled_source"] = pytest.mappings['prefilled_source']['OTHER']
        elif test_data['test_type'] == pytest.mappings['lead_test_type']['WE_PREFILL_SUBMIT_LEAD']:
            test_data['sl_user_email'] = self.previous_email
            test_data['sl_user_phone'] = self.previous_phone
            test_data["prefilled_source"] = pytest.mappings['prefilled_source']['WEBENGAGE']
        elif (test_data['test_type'] == pytest.mappings['lead_test_type']['WE_LOGIN_AUH_PREFILL_SUBMIT_LEAD'] or
                test_data['test_type'] == pytest.mappings['lead_test_type']['LOGIN_AUH_PREFILL_SUBMIT_LEAD']):
            test_data['sl_user_email'] = sl_user_email
            test_data['sl_user_phone'] = sl_user_phone
            test_data["prefilled_source"] = pytest.mappings['prefilled_source']['AUH']
        elif test_data['test_type'] == pytest.mappings['lead_test_type']['WE_AUH_PREFILL_SUBMIT_LEAD']:
            pytest.driver.delete_all_cookies()
            test_data['sl_user_email'] = sl_user_email
            test_data['sl_user_phone'] = sl_user_phone
            test_data["prefilled_source"] = pytest.mappings['prefilled_source']['AUH']
        elif test_data['test_type'] == pytest.mappings['lead_test_type']['AUH_PREFILL_SUBMIT_LEAD']:    
            pytest.driver.delete_all_cookies()
            logout_webengage_user()
            test_data['sl_user_email'] = sl_user_email
            test_data['sl_user_phone'] = sl_user_phone
            test_data["prefilled_source"] = pytest.mappings['prefilled_source']['AUH']
        elif (test_data['test_type'] == pytest.mappings['lead_test_type']['WE_LOGIN_PREFILL_SUBMIT_LEAD'] or
                test_data['test_type'] == pytest.mappings['lead_test_type']['LOGIN_PREFILL_SUBMIT_LEAD']):
            if test_data['test_type'] == pytest.mappings['lead_test_type']['LOGIN_PREFILL_SUBMIT_LEAD']:
                pytest.driver.delete_all_cookies()
                logout_webengage_user()
            test_data['sl_user_email'] = login_credentials['sl_user_email']
            test_data['sl_user_phone'] = login_credentials['sl_user_phone']
            pytest.driver.get(pytest.config['prion_url'] + pytest.config['accounts_url']['login_page'])
            pg_login_page = LoginPage(pytest.driver)
            pg_login_page.login(test_data['sl_user_email'], login_credentials['password'])
            test_data["prefilled_source"] = pytest.mappings['prefilled_source']['LOGGED_IN']
        
        test_data["sl_user_email_hash"] = get_email_hash(test_data['sl_user_email'], test_data['sl_user_phone']);
        if test_data["prefilled_source"] == pytest.mappings['prefilled_source']['AUH']:
            self.url_data['Entry_Page'] = self.url_data['Entry_Page'] + "?#auh=" + test_data['sl_user_email_hash']

    def dynamo_lead_validation(self, testdata):
        time.sleep(30)
        """ time.sleep(200) #Time for the saveLead Logs to be added
        lead_id = None
        query = {}
        query['logGroupName'] = pytest.config['lead_create_log_group_name']
        query['startTime'] = int(round((time.time() - 2000) * 1000))
        query['endTime'] = int(round((time.time() + 2000) * 1000))
        query['queryString'] = pytest.config['lead_create_insights_api_response_fetch_query'].replace('sl_user_email', testdata['sl_user_email'].replace('.', '\\.').replace('+', '\\+'))
        response = CloudWatchInsights().fetch_records(query)
        if len(response['results']) == 0:
            pytest.fail("Lead Submitted but didn't create in Dynamo DB")
        else:
            lead_id = json.loads(response['results'][0][0]['value'])['data']['success'][0]['lead_id'] """

        lead_id=testdata['lead_id']
        
        query = {}
        query['table_name'] = 'Lead'
        query['attributes_to_get'] = testdata['dynamo_validation_fields']
        query['key_condition'] = {'lead_id': {"S" : lead_id}}

        dynamodb_response = DynamoDB().fetch_records(query)
        logging.warning(dynamodb_response)
        return dynamodb_response

    def salesforce_validation(self, testdata):
        sf = Salesforce(domain="example--partialqa.my",
            username='salesforceapi@example.com.partialqa', 
            password='exampleSfdc@123', 
            security_token='XWu4HDm8jFaPBqh7El5rKlEn3')
        
        query = "SELECT Id, "
        for field in testdata['salesforce_validation_fields']:
            query = query + field + ", "
        
        query = query[:-2]
        query = query +  " FROM Lead WHERE Id = '" + testdata['sfid'] + "'"

        sf_data = sf.query_all(query)
        logging.warning(sf_data)
    
   