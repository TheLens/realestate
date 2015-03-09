#!/usr/bin/python
# -*- coding: utf-8 -*-

import pprint
import base64
import httplib2
import mimetypes
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from apiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run

from app_config import gmail_username

pp = pprint.PrettyPrinter()

# Path to the client_secret.json file downloaded from the Developer Console
CLIENT_SECRET_FILE = 'key.json'

# Check https://developers.google.com/gmail/api/auth/scopes for all available scopes
OAUTH_SCOPE = 'https://www.googleapis.com/auth/gmail.compose'

# Location of the credentials storage file
STORAGE = Storage('gmail.storage')

# Start the OAuth flow to retrieve credentials
flow = flow_from_clientsecrets(CLIENT_SECRET_FILE, scope=OAUTH_SCOPE)
http = httplib2.Http()

# Try to retrieve credentials from storage or run the flow to generate them
credentials = STORAGE.get()
if credentials is None or credentials.invalid:
  credentials = run(flow, STORAGE, http=http)

# Authorize the httplib2.Http object with our credentials
http = credentials.authorize(http)

# Build the Gmail service from discovery
gmail_service = build('gmail', 'v1', http=http)

yesterday_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

def CreateMessage(sender = 'Thomas Thoren <tthoren@thelensnola.org>', to = 'Thomas Thoren <tthoren@thelensnola.org>', initial_date = yesterday_date, until_date = yesterday_date):
    """
    Create a message for an email.

    Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.

    Returns:
    An object containing a base64url encoded email object.
    """
    stats_file = "email-%s.txt" % datetime.now().strftime('%Y-%m-%d')

    stats_dir = "logs/" + stats_file
    f_stats = open(stats_dir, 'r')

    log_file = "land-records_%s.log" % datetime.now().strftime('%Y-%m-%d')

    log_dir = "logs/" + log_file

    message = ''

    for line in f_stats:
        message = message + line

    message_text = message

    message = MIMEMultipart()

    message['to'] = to
    message['from'] = sender

    if initial_date == until_date:
        message['subject'] = "Land records summary for sales recorded " + (datetime.strptime(initial_date, '%Y-%m-%d')).strftime('%A, %b. %-d, %Y')
    else:
        initial_date = (datetime.strptime(initial_date, '%Y-%m-%d')).strftime('%A, %b. %-d, %Y')
        until_date = (datetime.strptime(until_date, '%Y-%m-%d')).strftime('%A, %b. %-d, %Y')

        message['subject'] = "Land records summary for sales recorded between " + initial_date + " and " + until_date

    msg = MIMEText(message_text, 'html')
    message.attach(msg)

    if to == 'Thomas Thoren <tthoren@thelensnola.org>':
          '''
          Only attach log file for email sent to me.
          '''
          content_type, encoding = mimetypes.guess_type(log_dir)

          if content_type is None or encoding is not None:
            content_type = 'application/octet-stream'
          main_type, sub_type = content_type.split('/', 1)
          fp = open(log_dir, 'rb')
          msg = MIMEText(fp.read(), _subtype=sub_type)
          fp.close()

          msg.add_header('Content-Disposition', 'attachment', filename=log_file)
          message.attach(msg)

    return {
        'raw': base64.urlsafe_b64encode(message.as_string())
        }

def SendMessage(service, user_id, message_body):
    """
    Create and insert a draft email. Print the returned draft's message and id.

    Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    message_body: The body of the email message, including headers.

    Returns:
    Draft object, including draft id and message meta data.
    """

    #todo: need way to truncate if too large. will only ever be a problem for full rebuild, but still, need to make that process as failproof as possible.
    message = (service.users().messages().send(userId=user_id, body=message_body).execute())

    return message
    
def main(initial_date = yesterday_date, until_date = yesterday_date):

    '''
    # Don't include log file so the email doesn't get placed in spam folder
    # todo: turn this back on so other people can receive email notifications
    them_message = CreateMessage(
        sender = 'Thomas Thoren <tthoren@thelensnola.org>',
        to = 'Abe Handler <ahandler@thelensnola.org>, Charles Maldonado <cmaldonado@thelensnola.org>, Steve Myers <smyers@thelensnola.org>'
    )
    SendMessage(gmail_service, gmail_username, them_message)
    '''

    me_message = CreateMessage(
        sender = 'Thomas Thoren <tthoren@thelensnola.org>',
        to = 'Thomas Thoren <tthoren@thelensnola.org>',
        initial_date = initial_date,
        until_date = until_date
    )
    SendMessage(gmail_service, gmail_username, me_message)

if __name__ == '__main__':
    main()
