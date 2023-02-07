#!/usr/bin/env python
# encoding: utf-8
import json
import os
from typing import Union

from fastapi import FastAPI, HTTPException
from fastapi.openapi.utils import get_openapi
from imapreader import IMAPReader

app = FastAPI()


def my_schema():
   openapi_schema = get_openapi(
       title="IMAP to JSON API",
       version="1.0",
       description="Retrieve emails from an IMAP mail server",
       routes=app.routes,
   )
   app.openapi_schema = openapi_schema
   return app.openapi_schema

app.openapi = my_schema

email_id = os.environ['EMAIL_ID']
email_pass = os.environ['EMAIL_PASS']
email_host = os.environ['EMAIL_HOST']

reader = IMAPReader(email_id=email_id, email_password=email_pass, email_host=email_host)

@app.get('/')
def index():
    return json.dumps({'version': '1.0.0'})

@app.get('/messages/latest')
def get_latest():
  """Get the latest / most recent message in the mailbox"""
  reader.login()
  message = reader.get_mail()[0]
  subject = message.get('Subject')
  date = message.get('Date')
  email_from = message.get('From')
  email_to = message.get('To')
  email_body = reader.get_email_body(message, format='plain')

  reader.close()
  
  return json.dumps({
    'to': email_to,
    'from': email_from,
    'subject': subject,
    'date': date,
    'body': email_body
    })

@app.get('/messages/all')
def get_all():
  """Get all messages in the mailbox"""
  _ = reader.login()
  messages = reader.get_mail()

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
  
  reader.close()
  return json.dumps(messages_dict)

@app.get('/messages/last')
def get_last_n_messages(count: int = 1): 
  """Get the last n most recent messages in the mailbox"""
  _ = reader.login()
  messages = reader.get_mail()[:count]

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
  
  reader.close()
  return json.dumps(messages_dict)

@app.get('/messages/search')
def search_by(subject: Union[str, None] = None, 
    body: Union[str, None] = None, 
    datetime: Union[str, None] = None):
  """Search by subject, body or date"""
  
  subject_unsanitized = subject
  body_unsanitized = body
  datetime_unsanitized = datetime

  reader.login()

  parameter_count = 0
  if subject_unsanitized != None:
    parameter_count += 1

  if body_unsanitized != None:
    parameter_count += 1
  
  if datetime_unsanitized != None:
    parameter_count += 1
  
  if parameter_count > 1:
    raise HTTPException(status_code = 400, detail = "Too many paremeters received.")
  
  # Subject only
  if subject_unsanitized and not body_unsanitized and not datetime_unsanitized:
    messages = reader.get_emails_with_subject(subject_unsanitized)
  # Body only
  elif body_unsanitized and not subject_unsanitized and not datetime_unsanitized:
    messages = reader.get_emails_with_body(body_unsanitized)
  # Date / time only
  elif datetime_unsanitized and not subject_unsanitized and not body_unsanitized:
    messages = reader.get_emails_since_date(datetime_unsanitized)
  else:
    raise HTTPException(status_code = 400, detail = "subject, body or datetime is required")

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
  reader.close()
  return json.dumps(messages_dict)
