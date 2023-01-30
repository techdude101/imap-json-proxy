#!/usr/bin/env python
# encoding: utf-8
import json
import os
from flask import Flask

from imapreader import IMAPReader

app = Flask(__name__)


email_id = os.environ['EMAIL_ID']
email_pass = os.environ['EMAIL_PASS']
email_host = os.environ['EMAIL_HOST']

reader = IMAPReader(email_id=email_id, email_password=email_pass, email_host=email_host)

@app.route('/', methods=['GET'])
def index():
    return json.dumps({'version': '1.2.3'})

@app.route('/messages/latest')
def get_latest():
  message = reader.get_mail()[-1]
  subject = message.get('Subject')
  date = message.get('Date')
  email_from = message.get('From')
  email_to = message.get('To')
  email_body = reader.get_email_body(message)
  
  return json.dumps({
    'to': email_to,
    'from': email_from,
    'subject': subject,
    'date': date,
    'body': email_body
    })

@app.route('/messages/all')
def get_all():
  messages = reader.get_mail()
  messages_dict = []
  for message in messages:
    subject = message.get('Subject')
    date = message.get('Date')
    email_from = message.get('From')
    email_to = message.get('To')
    email_body = reader.get_email_body(message)
    message_dict = {
    'to': email_to,
    'from': email_from,
    'subject': subject,
    'date': date,
    'body': email_body
    }
    messages_dict.append(message_dict)
  
  return json.dumps(messages_dict)


app.run(host='0.0.0.0')