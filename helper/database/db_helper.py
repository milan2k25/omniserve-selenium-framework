from .db_connection import database_factory
from . import utils
import logging
from typing import Any

'''
    Query data from test environment.

    Params 

        query [str] : Query to execute and fetch data .  
        db_type [str] : (Default:'my_sql') The source database to connect.
        format_dict [bool] : (Default:True) If True -> list of (key:columns, val:records) pairs
                                If False -> A list(tuple(records))

    Returns:

        type: dict / list (format_dict = False)
        A list of dictionary with the fetched records [ key-value pairs ] 
        Or list of fetched records
'''
def get_test_data(query: Any,db_type:str ='mysql', format_dict:bool = True):   
 
    CONFIG = utils.fetch_config(path = "helper\database\config.json")
    #logging.info(f" DB_type selected : {db_type} ")
    return _get_data(db_type,CONFIG[db_type],query,format_dict)

'''
    Query data from prod environment.

    Params 

        query [string] : Query to execute and fetch data .  
        db_type [str] : (Default:'my_sql') The source database to connect.
        format_dict [bool] : (Default:True) If True -> list of (key:columns, val:records) pairs
                                If False -> list of records, in which 1 row would be columns

    Returns:
    
        type: dict / list (format_dict = False)
        A list of dictionary with the fetched records [ key-value pairs ] 
        Or list of fetched records
'''    
def get_prod_data(query: Any,db_type:str ='mysql',format_dict:bool = True):    
    CONFIG = utils.fetch_config(path = "helper\database\config_prod.json")
    #logging.info(f" DB_type selected : {db_type} ")
    return _get_data(db_type,CONFIG[db_type],query,format_dict)

def insert_data(query: str,db_type:str ='mysql',format_dict:bool = True):
    CONFIG = utils.fetch_config(path = "helper\\database\\config.json")
    logging.info(f" DB_type selected : {db_type} ")
    with database_factory(db_type, CONFIG[db_type]) as connection :
        return connection.insert_records(query,format_dict)
     
def _get_data(type,connection_string,query,format_dict):
    with database_factory(type,connection_string) as connection :
        return connection.fetch_records(query,format_dict)              


    







