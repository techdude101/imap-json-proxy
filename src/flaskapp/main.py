
import os
from imapreader import IMAPReader
import email
from email.policy import default as default_policy

if __name__ == '__main__':
  email_examples_path = os.path.join(os.getcwd(), 'email_examples')
  filename = 'email_with_html.txt'
  
  reader = IMAPReader(email_id="", email_password="", email_host="")

  email_body = ""
  # when
  with open(os.path.join(email_examples_path, filename), 'r') as email_file:
    message = email.message_from_string(email_file.read(), policy=default_policy)
    email_body = reader.get_email_body(message)
    print(email_body)