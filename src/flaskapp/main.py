
import os
from imapreader import IMAPReader
import email
from email.policy import default as default_policy

if __name__ == '__main__':
  email_examples_path = os.path.join(os.getcwd(), 'email_examples')
  filename = 'email_with_html.txt'
  
  reader = IMAPReader(email_id="", email_password="", email_host="")

  email_body = ""

  print(reader.iso8601_datetime_to_rfc2822_date_string("2023-02-04T15:26:44.920Z"))