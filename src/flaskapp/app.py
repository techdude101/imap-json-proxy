#!/usr/bin/env python
# encoding: utf-8
import os
import sys
import uvicorn
import logging
import imaplib
from typing import Union

from fastapi import FastAPI, HTTPException
from fastapi.openapi.utils import get_openapi
from imapreader import IMAPReader
from helpers import email_messages_to_messages_dict

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

try:
  email_id = os.environ['EMAIL_ID']
  email_pass = os.environ['EMAIL_PASS']
  email_host = os.environ['EMAIL_HOST']
except KeyError:
  sys.exit("Missing required environment variables: EMAIL_ID, EMAIL_PASS and / or EMAIL_HOST")


reader = IMAPReader(email_id=email_id, email_password=email_pass, email_host=email_host)

@app.get('/')
def index():
    return{'version': '0.1.3-alpha'}

@app.get('/messages/latest')
def get_latest():
  """Get the latest / most recent message in the mailbox"""
  try:
    reader.login()
  except imaplib.IMAP4.error as error:
    # Strip b'' from error message e.g. b'LOGIN failed.' becomes LOGIN failed.
    error_message = str(error).replace("b'", "").replace("'", "")
    raise HTTPException(status_code = 500, detail = f"Something went wrong ... {error_message}")
  
  message = reader.get_mail()[0]
  subject = message.get('Subject')
  date = message.get('Date')
  email_from = message.get('From')
  email_to = message.get('To')
  email_body = reader.get_email_body(message, format='plain')

  reader.close()
  
  return {
    'to': email_to,
    'from': email_from,
    'subject': subject,
    'date': date,
    'body': email_body
    }

@app.get('/messages/all')
def get_all():
  """Get all messages in the mailbox"""
  try:
    reader.login()
  except imaplib.IMAP4.error as error:
    # Strip b'' from error message e.g. b'LOGIN failed.' becomes LOGIN failed.
    error_message = str(error).replace("b'", "").replace("'", "")
    raise HTTPException(status_code = 500, detail = f"Something went wrong ... {error_message}")
  messages = reader.get_mail()

  messages_dict = email_messages_to_messages_dict(reader, messages)
  
  reader.close()
  return messages_dict

@app.get('/messages/last')
def get_last_n_messages(count: int = 1): 
  """Get the last n most recent messages in the mailbox"""
  try:
    reader.login()
  except imaplib.IMAP4.error as error:
    # Strip b'' from error message e.g. b'LOGIN failed.' becomes LOGIN failed.
    error_message = str(error).replace("b'", "").replace("'", "")
    raise HTTPException(status_code = 500, detail = f"Something went wrong ... {error_message}")
  messages = reader.get_mail()[:count]

  messages_dict = email_messages_to_messages_dict(reader, messages)
  
  reader.close()
  return messages_dict

@app.get('/messages/search')
def search_by(subject: Union[str, None] = None, 
    body: Union[str, None] = None, 
    datetime: Union[str, None] = None):
  """Search by subject, body or date"""
  
  subject_unsanitized = subject
  body_unsanitized = body
  datetime_unsanitized = datetime

  parameter_count = 0
  if subject_unsanitized != None:
    parameter_count += 1

  if body_unsanitized != None:
    parameter_count += 1
  
  if datetime_unsanitized != None:
    parameter_count += 1
  
  if parameter_count > 1:
    raise HTTPException(status_code = 400, detail = "Too many paremeters received.")

  try:
    reader.login()
  except imaplib.IMAP4.error as error:
    # Strip b'' from error message e.g. b'LOGIN failed.' becomes LOGIN failed.
    error_message = str(error).replace("b'", "").replace("'", "")
    raise HTTPException(status_code = 500, detail = f"Something went wrong ... {error_message}")

  # Subject only
  if subject_unsanitized and not body_unsanitized and not datetime_unsanitized:
    messages = reader.get_emails_with_subject(subject_unsanitized)
  # Body only
  elif body_unsanitized and not subject_unsanitized and not datetime_unsanitized:
    messages = reader.get_emails_with_body(body_unsanitized)
  # Date / time only
  elif datetime_unsanitized and not subject_unsanitized and not body_unsanitized:
    try:
      messages = reader.get_emails_since_date(datetime_unsanitized)
    except ValueError as error:
      raise HTTPException(status_code = 400, detail = "Invalid ISO 8601 string")  
  else:
    raise HTTPException(status_code = 400, detail = "subject, body or datetime is required")

  messages_dict = email_messages_to_messages_dict(reader, messages)

  reader.close()
  return messages_dict


def main():
  logging.basicConfig(
    filename='flaskapp.log', 
    datefmt='%Y-%m-%d %H:%M:%S', 
    format='%(asctime)s %(levelname)s:%(message)s', 
    level=logging.DEBUG
    )
  logging.info('Starting service')
  
  uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)

  logging.info('Service stopped')

if __name__ == '__main__':
  main()