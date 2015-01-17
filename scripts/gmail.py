#!/usr/bin/python
# -*- coding: utf-8 -*-

import pprint
import base64
import httplib2
from datetime import datetime
from email.mime.text import MIMEText
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

def CreateMessage(sender, to, rows):
  """Create a message for an email.

  Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.

  Returns:
    An object containing a base64url encoded email object.
  """

  subject = "Land records summary -- " + datetime.now().strftime('%Y-%m-%d')

  message = ''
  for row in rows:
    message = message + '\n\n' + ',\n'.join("%s: %r" % (key, val) for (key, val) in row.iteritems())
  message_text = message#todo: use json module to convert to string

  message = MIMEText(message_text)

  message['to'] = 'tthoren@thelensnola.org'
  message['from'] = 'tthoren@thelensnola.org'
  message['subject'] = subject
  return {'raw': base64.urlsafe_b64encode(message.as_string())}

def SendMessage(service, user_id, message_body):
    """Create and insert a draft email. Print the returned draft's message and id.

    Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    message_body: The body of the email message, including headers.

    Returns:
    Draft object, including draft id and message meta data.
    """

    message = (service.users().messages().send(userId=user_id, body=message_body).execute())

    return message
    
def main(rows):

  message = CreateMessage('tthoren@thelensnola.org', 'tthoren@thelensnola.org', rows)
  SendMessage(gmail_service, gmail_username, message)

if __name__ == '__main__':
  main()
