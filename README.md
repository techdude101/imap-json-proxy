# IMAP JSON Proxy

Service to retrieve emails via HTTP methods  

- [x] Get all emails  
- [x] Get first (latest) email  
- [x] Get first x (latest x number of) emails  
- [x] Get emails from specified date until now
- [x] Search for emails by subject  
- [x] Search for emails by body content  

## Setup
`python -m venv venv`  
`venv/bin/pip install -r requirements.txt`  

## Start the service

1. Set environment variables  
`set EMAIL_ID=<email@host.domain>`  
`set EMAIL_PASS=<password>`  
`set EMAIL_HOST=<imap.gmail.com>`  

2. Start the service  
`venv/bin/python app.py`  