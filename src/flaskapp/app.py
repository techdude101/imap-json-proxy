#!/usr/bin/env python
# encoding: utf-8
import json
import os
from flask import Flask, request

from imapreader import IMAPReader
from responses import generate_bad_request

app = Flask(__name__)


email_id = os.environ['EMAIL_ID']
email_pass = os.environ['EMAIL_PASS']
email_host = os.environ['EMAIL_HOST']

reader = IMAPReader(email_id=email_id, email_password=email_pass, email_host=email_host)

@app.route('/', methods=['GET'])
def index():
    return json.dumps({'version': '1.0.0'})

@app.route('/messages/latest', methods=['GET'])
def get_latest():
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

@app.route('/messages/all', methods=['GET'])
def get_all():
  response = reader.login()
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

@app.route('/messages/last', methods=['GET'])
def get_last_n_messages():
  count_unsanitized = request.args.get('count', None)
  count = 1
  try:
    count = int(count_unsanitized)
  except ValueError:
    return generate_bad_request("count validation error")
  
  response = reader.login()
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

@app.route('/messages/search', methods=['GET'])
def search_by():
  subject_unsanitized = request.args.get('subject', None)
  body_unsanitized = request.args.get('body', None)
  datetime_unsanitized = request.args.get('datetime', None)
  
  reader.login()
  if subject_unsanitized and not body_unsanitized and not datetime_unsanitized:
    messages = reader.get_emails_with_subject(subject_unsanitized)
  elif body_unsanitized and not subject_unsanitized and not datetime_unsanitized:
    messages = reader.get_emails_with_body(body_unsanitized)
  elif datetime_unsanitized and not subject_unsanitized and not body_unsanitized:
    messages = reader.get_emails_since_date(datetime_unsanitized)
  else:
    return generate_bad_request("subject, body or datetime is required")

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

app.run(host='0.0.0.0')