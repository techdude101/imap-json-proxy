from imaplib import IMAP4_SSL
from email.policy import default as default_policy
import email
from datetime import datetime

class IMAPReader:
  def __init__(self, email_id="", email_password="", email_host="", port = 993):
    self.email_id = email_id
    self.email_password = email_password
    self.email_host = email_host
    self.port = port

  def login(self):
    """Connect and login to IMAP server

    Args:
      None

    Returns:
      tuple[Literal['OK'], list[bytes]]

    Raises:
      IMAP4.error: Exception raised on any errors.
    """
    self.imap4_ssl = IMAP4_SSL(self.email_host, self.port)
    response = self.imap4_ssl.login(self.email_id, self.email_password)
    return response

  def close(self):
    """Logout and close the connection to the IMAP server"""
    self.imap4_ssl.close()
    self.imap4_ssl.logout()

  def select_mailbox_and_get_email_count_in_mailbox(self, mailbox_name: str = 'INBOX') -> tuple:
    """Selects a given mailbox and get the number of emails in the given mailbox

    Args:
      mailbox_name: (optional) Mailbox name. Defaults to INBOX

    Returns:
      Tuple of response code and count of emails in mailbox

    Raises:
      imaplib.IMAP4.error: Exception raised on any errors.
    """
    response_code, mail_count = self.imap4_ssl.select(mailbox=mailbox_name, readonly=True)
    return (response_code, mail_count)
  

  def get_mail(self, mailbox: str = 'INBOX') -> list:
    """Get all messages in mailbox

    Args:
      None
    
    Returns:
      List of email.message.Message
    """
    messages = []

    self.select_mailbox_and_get_email_count_in_mailbox()
    
    response_code, mail_ids = self.imap4_ssl.search(None, 'ALL')

    messages = self.fetch_emails(mail_ids)

    # Reverse the list so emails are sorted newest to oldest
    messages.reverse() 
    return messages

  def get_email_body(self, message: email.message.EmailMessage, format: str="") -> str:
    """Extract email body from a given message

    Args:
      message: Email message
    
    Returns:
      Email body as a string

    Raises:
      AttributeError: 
    """
    message_type_is_valid = isinstance(message, email.message.EmailMessage)
    if not message_type_is_valid:
      raise AttributeError('Invalid "message" type. Expected type to be email.message.EmailMessage')
    if format == 'plain' or format == 'html':
      email_body = message.get_body(preferencelist=(format)).as_string()
      body = email_body.split('\n\n', 1)[1]
    else:
      raise AttributeError('Invalid "format". Expected plain or html')
    return body

  def get_emails_with_subject(self, search_string: str, mailbox: str = 'INBOX'):
    """Get emails with subject containing <search string>

    Args:
      search_string: String to search for email subject

    Returns:
      List of email.messages.Message
    """
    messages = []

    self.select_mailbox_and_get_email_count_in_mailbox()
    
    response_code, mail_ids = self.imap4_ssl.search(None, 'SUBJECT', search_string)

    messages = self.fetch_emails(mail_ids)

    # Reverse the list so emails are sorted newest to oldest
    messages.reverse() 
    return messages

  def get_emails_with_body(self, search_string, mailbox='INBOX') -> list:
    """Get emails with body containing <search string>

    Args:
      search_string: String to search for email body

    Returns:
      List of email.messages.Message
    """
    messages = []

    self.select_mailbox_and_get_email_count_in_mailbox()
    
    response_code, mail_ids = self.imap4_ssl.search(None, 'BODY', search_string)
    
    messages = self.fetch_emails(mail_ids)

    # Reverse the list so emails are sorted newest to oldest
    messages.reverse() 
    return messages

  def get_emails_since_date(self, start_date, mailbox='INBOX'):
    """Get emails since <date and time in ISO 8601 format>

    Args:
      start_date: Start date and time in ISO 8601 format

    Returns:
      List of email.messages.Message
    """
    messages = []

    self.select_mailbox_and_get_email_count_in_mailbox()

    formatted_start_date = self.iso8601_datetime_to_rfc2822_date_string(start_date)
    
    # IMAP protocol - https://www.rfc-editor.org/rfc/rfc3501#section-6.4.4
    # Date format - https://www.rfc-editor.org/rfc/rfc2822#section-3.3
    # SEARCH SINCE 1-Feb-1994
    response_code, mail_ids = self.imap4_ssl.search(None, 'SINCE', formatted_start_date)
    messages = self.fetch_emails(mail_ids)

    # Reverse the list so emails are sorted newest to oldest
    messages.reverse() 
    return messages


  def fetch_emails(self, mail_ids):
    """Fetch emails from server given a list of mail IDs

    Args:
      mail_ids: A list of mail IDs

    Returns:
      List of email.message.Message.

    Raises:
      IMAP4.error: Exception raised on any errors. The reason for the exception is passed to the constructor as a string.
      IMAP4.abort: IMAP4 server errors cause this exception to be raised.
    """
    messages = []

    # Sample response -> ('OK', [b'1 2 3 4 5'])
    # response_code, mail_ids = ('OK', [b'1 2 3 4 5'])
    for mail_id in mail_ids[0].decode('utf-8').split():
      response_code, mail_data = self.imap4_ssl.fetch(mail_id, '(RFC822)')
      message = email.message_from_bytes(mail_data[0][1], policy=default_policy)
      messages.append(message)
    return messages

  def iso8601_datetime_to_rfc2822_date_string(self, iso_date_time_string):
    """Converts a date / time string in ISO 8601 format to RFC2822 Date format

    Args:
      iso_date_string: A date / time string in ISO 8601 format.

    Returns:
      Date in RFC2822 format.

    Raises:
      ValueError: If invalid date / time string is provided.
    """
    rfc2822_date_string = ""
    if not isinstance(iso_date_time_string, str):
      raise ValueError("Invalid ISO 8601 string")
    iso_date_string = iso_date_time_string.split("T")[0]

    try:
      date_object = datetime.strptime(iso_date_string, "%Y-%m-%d")
      rfc2822_date_string = date_object.strftime("%d-%b-%Y")
    except ValueError:
      raise ValueError("Invalid ISO 8601 string")
    return rfc2822_date_string