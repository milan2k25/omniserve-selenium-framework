import logging
from operator import itemgetter
import os
from utility.utils import ProductData
import pytest
import sys
import json
# importing ObjectId from bson library
from bson.objectid import ObjectId

sys.path[0] = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)))

import helper.database.db_helper as db

def article_amp_check(urls_list):
    query = {}
    query['database_name'] = 'caldon'
    query['collection_name'] = 'contents'
    query['query_type'] = 'find'
    query['query'] = {'type':'article', 'status':4, 'seo_url':{'$in':urls_list}, 'is_amp_page':True}
    query['project'] = {"seo_url":1, "_id":0}
    logging.warning(query)
    response_data = db.get_test_data(query, 'mongo')
    response = list(map(itemgetter('seo_url'), response_data))
    return response
    
#Extract the documents from mongo DB to get the jumplinks data on the basis of FRS type.
def get_contents_with_frs_type(page_type,projection):
    query = {}
    query['database_name'] = 'caldon'
    query['collection_name'] = 'contents'
    query['query_type'] = 'find'
    query['query'] = {'type':page_type, 'status': 4}
    query['project'] = projection
    response_data = db.get_test_data(query, 'mongo') 
    if len(response_data) > 0:
        return response_data
    else:
        return []

def get_contents_with_frs_type_by_id(page_type, resource_id, projection):
    query = {}
    query['database_name'] = 'caldon'
    query['collection_name'] = 'contents'
    query['query_type'] = 'find'
    query['query'] = {'type':page_type, 'status': 4, '_id' : ObjectId(resource_id)}
    query['project'] = projection
    response_data = db.get_test_data(query, 'mongo') 
    if len(response_data) > 0:
        return response_data
    else:
        return []

def get_banner_information_by_id(banner_id, projection):
    query = {}
    query['database_name'] = 'caldon'
    query['collection_name'] = 'banners'
    query['query_type'] = 'find'
    query['query'] = {'status': 1, '_id' : ObjectId(banner_id)}
    query['project'] = projection
    response_data = db.get_test_data(query, 'mongo') 
    if len(response_data) > 0:
        return response_data
    else:
        return []

def get_banner_id_from_resource_banner_mapping(resource_id, projection):
    query = {}
    query['database_name'] = 'caldon'
    query['collection_name'] = 'banner_resources'
    query['query_type'] = 'find'
    query['query'] = {'resource_id':resource_id, 'status': 1}
    query['project'] = projection
    response_data = db.get_test_data(query, 'mongo') 
    if len(response_data) > 0:
        return response_data
    else:
        return []

def is_b2b_resource(data, frs_type):
    if frs_type == 'tutorial':
        homepage_data = get_contents_with_frs_type_by_id('video_homepage', data[0]['videoplaylistId'], {'_id' : 0, 'segments' : 1})
        data[0]['segments'] = homepage_data[0]['segments'][0]
    return True if data[0]['segments'] in [34, 35] else False

def get_banner_resource_mapping_data_by_resource_type(frs_type, projection):
    query = {}
    query['database_name'] = 'caldon'
    query['collection_name'] = 'banner_resources'
    query['query_type'] = 'find'
    query['query'] = {'resource_type':frs_type, 'status': 1}
    query['project'] = projection
    response_data = db.get_test_data(query, 'mongo') 
    if len(response_data) > 0:
        return response_data
    else:
        return []

def get_resources_with_formbanner_enabled(frs_type):
    banner_resource_response_data = get_banner_resource_mapping_data_by_resource_type(frs_type, {'resource_id':1, 'banner_id':1, '_id':0})
    
    for index in sorted(range(len(banner_resource_response_data)), reverse=True):
        banner_response_data = get_banner_information_by_id(banner_resource_response_data[index]['banner_id'], {'banner_type':1, 'banner_product_type': 1, 'banner_product_id': 1, 'site_module': 1})
        if (len(banner_response_data) > 0 and banner_response_data[0]['banner_type'] != 'form') or (len(banner_response_data) == 0):
            del banner_resource_response_data[index]
        else:
            content_response_data = get_contents_with_frs_type_by_id(frs_type, banner_resource_response_data[index]['resource_id'], {'_id' : 0, 'segments' : 1, 'canonical' : 1, 'primary_product_id' : 1, 'primary_product_type' : 1, 'videoplaylistId' : 1})
            if len(content_response_data) > 0:
                content_response_data[0]['segments'] = content_response_data[0]['segments'][0] if 'segments' in content_response_data[0] else 0
                content_response_data[0]['is_b2b'] = is_b2b_resource(content_response_data, frs_type)
                content_response_data[0]['Entry_Page'] = pytest.config['sheldon_url'][:-1] + "/" + content_response_data[0]['canonical'].replace('%2F', '/').lstrip('/')
                
                country_code_id_mapping = pytest.config['country_code_id_mapping']
                content_response_data[0]['mql_banner_countries'] = []
                content_response_data[0]['mql_form_countries'] = []
                content_response_data[0]['banner_product_id'] = banner_response_data[0]['banner_product_id']
                content_response_data[0]['banner_product_type'] = banner_response_data[0]['banner_product_type']
                content_response_data[0]['banner_site_module'] = banner_response_data[0]['site_module']

                for country_code, country_id in country_code_id_mapping.items():
                    category_information = ProductData().get_product_details(banner_response_data[0]['banner_product_id'], country_id, banner_response_data[0]['banner_product_type'])
                    if category_information:
                        override_sitemodule = get_override_sitemodule(country_id, frs_type, banner_response_data[0]['banner_product_type'], banner_response_data[0]['banner_product_id'], category_information[1], 'category')
                        if override_sitemodule: content_response_data[0]['mql_banner_countries'].append(country_code)
                        
                    if 'primary_product_id' in content_response_data[0]:
                        category_information = ProductData().get_product_details(content_response_data[0]['primary_product_id'], country_id, content_response_data[0]['primary_product_type'])
                        if category_information:
                            override_sitemodule = get_override_sitemodule(country_id, frs_type, content_response_data[0]['primary_product_type'], content_response_data[0]['primary_product_id'], category_information[1], 'category')
                            if override_sitemodule: content_response_data[0]['mql_form_countries'].append(country_code)
                
                banner_resource_response_data[index].update(content_response_data[0])
            else:
                del banner_resource_response_data[index]

    return banner_resource_response_data

def is_form_banner_enabled(resource_id):
    banner_id = get_banner_id_from_resource_banner_mapping(resource_id, {'_id': 0, 'banner_id': 1})
    banner_id = banner_id[0]['banner_id'] if len(banner_id) > 0 else 0
    if banner_id !=0:
        form_banner = get_banner_information_by_id(banner_id, {'banner_type': 1, '_id':0})
        return True if len(form_banner) > 0 and form_banner['banner_type'] == 'form' else False
    else:
        return False

#/sheldon/src/client/helpers/SLFunctions.js

def add_frs_data_to_json():
    frs_types = pytest.config["frs_types"]
    #frs_types= ["article", "ebook", "webinar", "tutorial", "video_homepage"]

    final_data = {}
    for frs_type in frs_types:
        final_data[frs_type] = get_resources_with_formbanner_enabled(frs_type)
    
    with open('utility/data/frs_data.json', 'w') as outfile:
        outfile.truncate(0)
        json.dump(final_data, outfile, indent=4)


def get_override_sitemodule(country_id, resource_type, product_type, product_id, category_id, label):
    override_sitemodule_data = {}
    sitemodule = ""
    override_sitemodule_exist = False
    if(resource_type == 'video_homepage'):
        resource_type = "tutorial"
    with open("utility/data/override_sitemodule.json",) as f:
        override_sitemodule_data = json.load(f)
        override_sitemodule_data = override_sitemodule_data['override_site_modules'][0]

    for key in override_sitemodule_data:
        if str(key) == str(country_id):
            if category_id and label and key in override_sitemodule_data and override_sitemodule_data[key] and resource_type in override_sitemodule_data[key] and override_sitemodule_data[key][resource_type] and label in override_sitemodule_data[key][resource_type] and override_sitemodule_data[key][resource_type][label] and int(override_sitemodule_data[key][resource_type][label]['enable']):
                    category_ids = override_sitemodule_data[key][resource_type][label]['id']
                    if str(category_id) in category_ids and override_sitemodule_data[key][resource_type][label]['sitemodule']:
                            sitemodule = override_sitemodule_data[key][resource_type][label]['sitemodule']
                            override_sitemodule_exist = True
            if not override_sitemodule_exist and key in override_sitemodule_data and override_sitemodule_data[key] and resource_type in override_sitemodule_data[key] and override_sitemodule_data[key][resource_type] and product_type in override_sitemodule_data[key][resource_type] and override_sitemodule_data[key][resource_type][product_type] and int(override_sitemodule_data[key][resource_type][product_type]['enable']):
                    course_ids = override_sitemodule_data[key][resource_type][product_type]['id']
                    if str(product_id) in course_ids and override_sitemodule_data[key][resource_type][product_type]['sitemodule']:
                        sitemodule = override_sitemodule_data[key][resource_type][product_type]['sitemodule']
                        override_sitemodule_exist = True
            break
    return sitemodule