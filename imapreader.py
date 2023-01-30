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



def main():
  email_id = "qatest49@outlook.com"
  email_pass = "u3sPzZQuYqFbnes"
  email_host = "outlook.office365.com"

  reader = IMAPReader(email_id=email_id, email_password=email_pass, email_host=email_host)
  messages = reader.get_mail()
  
  for message in messages:
    body = reader.get_email_body(message)
    body = body.split('\n\n', 1)[1]
    # body = ''.join(body)

    print(f"From      : {message.get('From')}")
    print(f"To        : {message.get('To')}")
    print(f"Date      : {message.get('Date')}")
    print(f"Subject   : {message.get('Subject')}")
    print(f"Body      : {body}")
    
    
    # for part in message.walk():
    #   if part.get_content_type() == "text/plain": ## Only Printing Text of mail.
    #       body_lines = part.as_string().split("\n")
    #       print("\n".join(body_lines))
  
  reader.close()
  

if __name__ == '__main__':
  main()