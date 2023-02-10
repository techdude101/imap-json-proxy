import email
from imapreader import IMAPReader

def email_messages_to_messages_dict(reader: IMAPReader, messages: email.message.Message) -> list:
  messages_dict = []
  for message in messages:
    subject = message.get('Subject')
    date = message.get('Date')
    email_from = message.get('From')
    email_to = message.get('To')
    email_body = reader.get_email_body(message, format='plain')
    message_dict = {
    'to': email_to,
    'from': email_from,
    'subject': subject,
    'date': date,
    'body': email_body
    }
    messages_dict.append(message_dict)
  return messages_dict