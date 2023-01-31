import re as regex
from imaplib import IMAP4_SSL
from email.policy import default as default_policy
import email

class IMAPReader:
  def __init__(self, email_id, email_password, email_host, port = 993):
    self.email_id = email_id
    self.email_password = email_password
    self.email_host = email_host
    self.port = port
    self.login()

  def login(self):
    """Connect and login to IMAP server"""
    self.mailbox = IMAP4_SSL(self.email_host, self.port)
    self.mailbox.login(self.email_id, self.email_password)

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
    return messages

  def get_email_body(self, message):
    """Extract email body from a given message"""
    email_body = message.get_body(preferencelist=('html', 'plain')).as_string()
    body = email_body.split('\n\n', 1)[1]
    return body
