import imaplib
import time
from email.header import decode_header
import email
import time,datetime,logging
import re


def get_url_lnk_from_email_body(user_email: str, password: str):

    '''
    Args :
        user_email (str) : Email Id of user
        password (str) : Password of user


    Returns :
        [str] : OTP

    '''
    time.sleep(5)
    try:
        # # Establish connection with Gmail
        server = "imap.gmail.com"
        # connection to the email server
        mail = imaplib.IMAP4_SSL(server)
        mail.login(user_email, password)
        mail.list()
        # Out: list of "folders" aka labels in gmail.
        mail.select("Inbox", readonly=True)  # connect to inbox.
        result, data = mail.uid('search', None, "ALL")  # search and return uids instead
        ids = data[0]  # data is a list.
        id_list = ids.split()  # ids is a space separated string
        latest_email_uid = data[0].split()[-1]
        result, data = mail.uid('fetch', latest_email_uid,'(RFC822)')  # fetch the email headers and body (RFC822) for the given ID
        raw_email = data[0][1]
        data = raw_email.decode('utf-8')
        verify_code = re.compile('<.*?>')
        code = re.sub(verify_code, '', str(data))
        otp_text = re.findall('Verification Code:(.*)', code)
        otp_text = otp_text[0].strip()

        return otp_text

    except Exception:
        pass

def get_webinar_link_from_email_body(user_email: str, password: str, email_subject: str, text: str, currenttime: datetime, link_start_text, link_end_text='<'):
    '''
    Args : 
        user_email (str) : Email Id of user
        password (str) : Password of user
        email_subject (str) : Subject of email
        text (str) : Text used in url of the link

    Returns :
        [str] : URL of the link

    '''

    email_date = datetime.datetime.now()
    # Establish connection with Gmail
    server = "imap.gmail.com"
    imap = imaplib.IMAP4_SSL(server)

    # login into the gmail account
    imap.login(user_email, password)

    # select inbox
    status, messages = imap.select("INBOX", "(UNSEEN)")

    # Iterate recent 3 mails
    N = 3
    messages = int(messages[0])
    for i in range(messages, messages-N, -1):

        # fetch the email message by ID
        res, msg = imap.fetch(str(i), "(RFC822)")
        for response in msg:
            if isinstance(response, tuple):

                # parse a bytes email into a message object
                msg = email.message_from_bytes(response[1])
                date_tuple = email.utils.parsedate_tz(msg['Date'])
                if date_tuple:
                    email_datetemp = datetime.datetime.fromtimestamp(
                        email.utils.mktime_tz(date_tuple))
                    email_date = email_datetemp

            # decode the email subject
            subject = decode_header(msg["Subject"])[0][0]

            if isinstance(subject, bytes):
                # if it's a bytes, decode to str
                subject = subject.decode()

            # get the email body
            body = msg.get_payload(decode=True)

            if isinstance(body, bytes):
                # if it's a bytes, decode to str
                body = body.decode()

            # get url_lnk from email body
            if email_subject in subject and email_date >= currenttime:
                logging.info('#################################')
                link_pattern = re.compile(
                    f'({link_start_text})(.*)?zoom.us(.+?){text}.[^{link_end_text}]*')
                search = link_pattern.search(body)
                url_link = search.group(0).replace("'", "")
                return url_link

    imap.close()