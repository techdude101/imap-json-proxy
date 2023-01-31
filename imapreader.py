import re as regex
from imaplib import IMAP4_SSL
from email.policy import default as default_policy
import email
from datetime import date, datetime

class IMAPReader:
  def __init__(self, email_id, email_password, email_host, port = 993):
    self.email_id = email_id
    self.email_password = email_password
    self.email_host = email_host
    self.port = port

  def login(self):
    """Connect and login to IMAP server"""
    self.mailbox = IMAP4_SSL(self.email_host, self.port)
    response = self.mailbox.login(self.email_id, self.email_password)
    return response

  def close(self):
    """Close connection to IMAP server"""
    self.mailbox.close()

  def get_mail(self, mailbox='INBOX'):
    """Get all messages in mailbox"""
    messages = []
    response_code, mail_count = self.mailbox.select(mailbox=mailbox, readonly=True)
    
    response_code, mail_ids = self.mailbox.search(None, 'ALL')
    for mail_id in mail_ids[0].decode('utf-8').split():
        response_code, mail_data = self.mailbox.fetch(mail_id, '(RFC822)')
        message = email.message_from_bytes(mail_data[0][1], policy=default_policy)
        messages.append(message)

    # Reverse the list so emails are sorted newest to oldest
    messages.reverse() 
    return messages

  def get_email_body(self, message):
    """Extract email body from a given message"""
    email_body = message.get_body(preferencelist=('html', 'plain')).as_string()
    body = email_body.split('\n\n', 1)[1]
    return body

  def get_emails_with_subject(self, subject, mailbox='INBOX'):
    """Get emails with subject containing <search string>"""
    messages = []
    response_code, mail_count = self.mailbox.select(mailbox=mailbox, readonly=True)
    
    response_code, mail_ids = self.mailbox.search(None, 'SUBJECT', subject)
    for mail_id in mail_ids[0].decode('utf-8').split():
        response_code, mail_data = self.mailbox.fetch(mail_id, '(RFC822)')
        message = email.message_from_bytes(mail_data[0][1], policy=default_policy)
        messages.append(message)
    # Reverse the list so emails are sorted newest to oldest
    messages.reverse() 
    return messages

  def get_emails_with_body(self, body, mailbox='INBOX'):
    """Get emails with body containing <search string>"""
    messages = []
    response_code, mail_count = self.mailbox.select(mailbox=mailbox, readonly=True)
    
    response_code, mail_ids = self.mailbox.search(None, 'BODY', body)
    for mail_id in mail_ids[0].decode('utf-8').split():
        response_code, mail_data = self.mailbox.fetch(mail_id, '(RFC822)')
        message = email.message_from_bytes(mail_data[0][1], policy=default_policy)
        messages.append(message)
    # Reverse the list so emails are sorted newest to oldest
    messages.reverse() 
    return messages

  def get_emails_since_date(self, start_date, mailbox='INBOX'):
    """Get emails since <date and time in ISO 8601 format>"""
    messages = []
    response_code, mail_count = self.mailbox.select(mailbox=mailbox, readonly=True)

    print(f"Start date: {start_date}")
    start_date_object = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S.%fZ")
    formatted_start_date = start_date_object.strftime("%d-%b-%Y")
    print(f"Formatted date: {formatted_start_date}")
    
    # IMAP protocol - https://www.rfc-editor.org/rfc/rfc3501#section-6.4.4
    # Date format - https://www.rfc-editor.org/rfc/rfc2822#section-3.3
    # SEARCH SINCE 1-Feb-1994
    response_code, mail_ids = self.mailbox.search(None, 'SINCE', formatted_start_date)
    # response_code, mail_ids = self.mailbox.search(None, 'SINCE', "1-Feb-1994")
    for mail_id in mail_ids[0].decode('utf-8').split():
        response_code, mail_data = self.mailbox.fetch(mail_id, '(RFC822)')
        message = email.message_from_bytes(mail_data[0][1], policy=default_policy)
        messages.append(message)
    # Reverse the list so emails are sorted newest to oldest
    messages.reverse() 
    return messages