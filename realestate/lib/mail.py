# -*- coding: utf-8 -*-

"""
A universal mail-sender, with methods for plain text, HTML and attachments.
"""

import os
import smtplib
import mimetypes
from os.path import basename
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from landrecords import log


class Mail(object):

    '''Mail methods include test, HTML and add attachments.'''

    def __init__(self,
                 subject="Land records summary",
                 body="Here is your email",
                 frm='tthoren@thelensnola.org',
                 to=['tthoren@thelensnola.org']):

        self.subject = subject
        self.body = body
        self.frm = frm
        self.to = to

    def send_email(self, msg):
        '''Initializes and sends the email.'''

        log.debug('Mail')

        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.ehlo()
        s.starttls()
        s.ehlo()
        s.login(os.environ.get('GMAIL_USERNAME'),
                os.environ.get('GMAIL_PASSWORD'))
        s.sendmail(self.frm, self.to, msg.as_string())
        s.quit()

    def add_headers(self, msg):
        '''Add email headers subject, from and to onto the message.'''

        msg['Subject'] = self.subject
        msg['From'] = self.frm
        msg['To'] = ','.join(self.to)

        return msg

    def send_as_text(self):
        '''Form plain text message.'''

        msg = MIMEText(self.body)

        msg = self.add_headers(msg)

        self.send_email(msg)

    def send_with_attachment(self, files=None):
        '''Attach file to message.'''

        msg = MIMEMultipart(self.body)

        msg = self.add_headers(msg)

        for f in files:
            content_type, encoding = mimetypes.guess_type(f)

            if content_type is None or encoding is not None:
                content_type = 'application/octet-stream'
            main_type, sub_type = content_type.split('/', 1)
            fp = open(f, 'rb')
            message = MIMEText(fp.read(), _subtype=sub_type)
            fp.close()

            message.add_header('Content-Disposition',
                               'attachment',
                               filename=basename(f))

            msg.attach(message)

        self.send_email(msg)

    def send_as_html(self):
        '''Form HTML message.'''

        msg = MIMEMultipart('alternative')

        msg = self.add_headers(msg)

        html = (
            '<!DOCTYPE html><html>' +
            '<head><meta charset="utf-8"></head>' +
            '<body>' +
            self.body +
            '</body></html>')

        msg_text = MIMEText(html, 'plain')
        msg_html = MIMEText(html, 'html')

        msg.attach(msg_text)
        msg.attach(msg_html)

        self.send_email(msg)

if __name__ == '__main__':
    pass
