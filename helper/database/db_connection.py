import mysql.connector
from interface import Interface, implements
import logging
from pymongo import MongoClient

def database_factory(db_type,connection_string):
    if db_type == 'mysql':
        return Mysql(connection_string)
    elif db_type == 'mongo':
        return Mongo(connection_string)
    else:
        raise TypeError(f"Argument type {db_type} is not of the expected type")


class Database(Interface):
    '''
    Database is the interface

    All other types of DB connection concrete class must inherit and implement the methods defined

    '''
    
    def __init__(self,connection_string):
        '''
        Database Initialization steps such as
        - establishing the connection
        - setting the cursor/reader
        - initiate with a config data for which the class methods will act upon

        connection_string: The connection details such as host,user,password etc.,
            type: Dictionary
        config: The details of table, query, search_key and columns to perform fetch/other operations
            type: Json/Dictionary
        '''
        pass

    def __enter__(self):
        '''
        This method will be executed before any other.
        Soon after object creation this method will be called.
        Include any setups if required
        '''
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        '''
        On object exit/end of scope this method will be called.
        the params give more info on any exception captured, caused by the instance of this class
        Include any cleanup, such as close() connection.

        exc_type: value will be passed as default by the program. Type of exception
        exc_val: value will be passed as default by the program. Base/Message of exception
        exc_tb: value will be passed as default by the program. Traceback (stack trace)

        '''
        pass

    def fetch_records(self,query):
        '''
        Params :

              query [string] : Query to execute and fetch data .
              format_dict [boolean] : Default is true . Returns fetched records in key(column) - value pairs respectively . 
        Returns:

              type: dict / list (format_dict = False)
              A list of dictionary with the fetched records [ key-value pairs ] 
              Or list of fetched records
        '''
        pass


class Mysql(implements(Database)):

    def __init__(self,connection_string):
        self.db =  mysql.connector.connect(**connection_string)
               
    def __enter__(self):
        #logging.info(" Mysql Connection is Established")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if (self.db.is_connected()):
            self.db.close()
            self.cursor.close()
        #logging.info(" Mysql Connection is closed ")
    
    def fetch_records(self,query,return_dict=True):
        self.cursor = self.db.cursor(dictionary=return_dict)
        self.cursor.execute(query)
        data = self.cursor.fetchall()
        return data

    def insert_records(self,query,return_dict=True):
        try:
            logging.info(f" Requested Query : {query}")
            self.cursor = self.db.cursor(dictionary=return_dict)
            self.cursor.execute(query)
            self.db.commit()
            return True
        except:
            return False

class Mongo(implements(Database)):

    def __init__(self,connection_string):
        self.client = MongoClient(connection_string['host'], connection_string['port'])
               
    def __enter__(self):
        #logging.info(" Mongo Connection is Established")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()
        #logging.info(" Mongo Connection is closed ")
    
    def fetch_records(self,query,return_dict=True):
        self.db = self.client[query['database_name']]
        self.collection = self.db[query['collection_name']]
        data = []
        if query['query_type'] == 'find':
            data = list(self.collection.find(query['query'], query['project']))
        elif query['query_type'] == 'find_with_limit':
            data = list(self.collection.find(query['query'], query['project']).limit(query['limit']))
        elif query['query_type'] == 'find_with_sort_limit':
            data = list(self.collection.find(query['query'], query['project']).limit(query['limit']).sort('welcome_class_starts_at',1))
        elif query['query_type'] == 'aggregate':
            data = list(self.collection.aggregate(query['query']))
        return data