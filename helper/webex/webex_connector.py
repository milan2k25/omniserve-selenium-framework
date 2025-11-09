import requests
from lxml import etree

# Change to true to enable request/response debug output
DEBUG = False

# Webex Meetings XML API uses securityContext to handle authentication and Webex site identification. 
# Every request must include securityContext. 
# Once the user is authenticated, the sessionTicket for all API requests will be stored here
sessionsecuritycontext = { }

# Custom exception for errors when sending requests
class SendRequestError(Exception):

    def __init__(self, result, reason):
        self.result = result
        self.reason = reason

# Generic function for sending XML API requests
# Params : envelope : the full XML content of the request
def send_request(url, envelope ):

    if DEBUG:
        print( envelope )

    # Use the requests library to POST the XML envelope to the Webex API endpoint
    headers = { 'Content-Type': 'application/xml'}
    response = requests.post(url, envelope,headers=headers )

    # Check for HTTP errors
    try: 
        response.raise_for_status()
    except requests.exceptions.HTTPError: 
        raise SendRequestError( 'HTTP ' + str(response.status_code), response.content.decode("utf-8") )

    # Use the lxml ElementTree object to parse the response XML
    message = etree.fromstring( response.content )

    if DEBUG:
        print( etree.tostring( message, pretty_print = True, encoding = 'unicode' ) )   

    # Use the find() method with an XPath to get the 'result' element's text
    # Note: {*} is pre-pended to each element name - ignores namespaces
    # If not SUCCESS...
    if message.find( '{*}header/{*}response/{*}result').text != 'SUCCESS':

        result = message.find( '{*}header/{*}response/{*}result').text
        reason = message.find( '{*}header/{*}response/{*}reason').text

        #...raise an exception containing the result and reason element content
        raise SendRequestError( result, reason )

    return message

"""

Authenticate_User

Converts Webex Teams API user password to a sessionTicket for XML API authentication

Params:

    sitename [type:string] :  Site name is the subgroup of the Webex site URL 
    webex_id  [type:string] : Username of the host or admin account making a request
    password [type:string] : The login password associated with the webExID

Returns:

    Response data is returned in XML format containing the security context info with sessionTicket

"""

def authenticate_user(url, sitename, webex_id, password ):

    request = f'''<?xml version="1.0" encoding="UTF-8"?>
            <serv:message xmlns:serv="http://www.webex.com/schemas/2002/06/service"
                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                <header>
                    <securityContext>
                        <siteName>{sitename}</siteName>
                        <webExID>{webex_id}</webExID>
                        <password>{password}</password>

                    </securityContext>
                </header>
                <body>
                    <bodyContent xsi:type="java:com.webex.service.binding.user.AuthenticateUser"/>
                </body>
            </serv:message>'''

    # Make the API request
    response = send_request(url, request )

    return {
            'siteName': sitename,
            'webExId': webex_id,
            'sessionTicket': response.find( '{*}body/{*}bodyContent/{*}sessionTicket' ).text
            }


'''
Create Meeting 

CreateMeeting enables users to schedule a meeting. This API returns a unique meeting key for the session i.e webex_session_id .

Params :

    sessionsecuritycontext [dict] : SecurityContext to handle authentication and Webex site identification .
    meetingpassword [string] : session password
    confname [string] : Name of the meeting
    agenda [string] : Agenda for the meeting.
    startdate [string] : Session startdate .

Returns:

    Response data is returned in XML format containing newly created webex_session_id .

'''
    
def create_meeting(url, sessionsecuritycontext,
                   meetingpassword,
                   confname,
                   agenda,
                   startdate ):

    request = f'''<?xml version="1.0" encoding="UTF-8"?>
        <serv:message xmlns:serv="http://www.webex.com/schemas/2002/06/service"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <header>
                <securityContext>
                    <siteName>{sessionsecuritycontext["siteName"]}</siteName>
                    <webExID>{sessionsecuritycontext["webExId"]}</webExID>
                    <sessionTicket>{sessionsecuritycontext["sessionTicket"]}</sessionTicket>  
                </securityContext>
            </header>
            <body>
                <bodyContent
                    xsi:type="java:com.webex.service.binding.meeting.CreateMeeting">
                    <accessControl>
                        <meetingPassword>{meetingpassword}</meetingPassword>
                    </accessControl>
                    <metaData>
                        <confName>{confname}</confName>      
                        <agenda>{agenda}</agenda>
                    </metaData>
                    <enableOptions>
                        <chat>true</chat>
                        <poll>true</poll>
                        <audioVideo>true</audioVideo>
                        <supportE2E>TRUE</supportE2E>
                        <autoRecord>TRUE</autoRecord>
                    </enableOptions>
                    <schedule>
                        <startDate>{startdate}</startDate>
                        <openTime>900</openTime>
                        <joinTeleconfBeforeHost>false</joinTeleconfBeforeHost>
                        <duration>20</duration>
                        <timeZoneID>4</timeZoneID>
                    </schedule>
                    <telephony>
                        <telephonySupport>CALLIN</telephonySupport>
                        <extTelephonyDescription>
                            Call 1-800-555-1234, Passcode 98765
                        </extTelephonyDescription>
                    </telephony>
                </bodyContent>
            </body>
        </serv:message>'''

    response = send_request(url,request)

    return response