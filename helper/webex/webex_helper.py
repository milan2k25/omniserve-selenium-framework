from datetime import date
import json
from . import utils
from . import webex_connector
import requests
import datetime
from lxml import etree


'''
    create_webex_session:

    create_webex_session api is used to create webex_session_id .

    Params :

    meetingpassword [str] : (Default:'C!sco123') The meeting password for the session.
    confname [str] : (Default:'Test Meeting') The conference name for the session. 
    agenda [str] : (Default:'Test Meeting creation') The meeting agenda.
    add_days [int] : (Default:0) The number of days to be added from the current date.

    Returns: 

    session_id [str] : The created session id from webex
'''   
def create_webex_session(meetingpassword: str = 'C!sco123',confname: str = 'Test Meeting',
            agenda: str = 'Test meeting creation',add_days:int=0):

    #region Init
    CONFIG = utils.fetch_config(path ='config.json')
    url = CONFIG['api_url']

    # AuthenticateUser and get session Ticket

    sessionsecuritycontext = webex_connector.authenticate_user(url,
        CONFIG['site_name'],
        CONFIG['webex_id'],
        CONFIG['password']
    )
    #endregion
    
    #region Create Meeting Date
    timestamp = datetime.datetime.now() + datetime.timedelta(days=add_days)

    # Create a string variable with the timestamp in the specific format required by the API
    start_date =  timestamp.strftime( '%m/%d/%Y %H:%M:%S' )
    #endregion

    #region Create Webex Session
    response = webex_connector.create_meeting( url,sessionsecuritycontext,
        meetingpassword = meetingpassword,
        confname = confname,
        agenda = agenda,
        startdate = start_date )

    return response.find('{*}body/{*}bodyContent/{*}meetingkey').text 
    #endregion