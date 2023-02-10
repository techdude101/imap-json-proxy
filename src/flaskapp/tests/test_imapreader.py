import unittest
import os
import email
import pytest
from email.policy import default as default_policy
from imaplib import IMAP4_SSL
from pytest import MonkeyPatch

# App imports
from imapreader import IMAPReader

class TestImapReader(object):
  reader = IMAPReader()

  email_examples_path = os.path.join(os.getcwd(), "..", "email_examples")
  
  @pytest.mark.parametrize(
    "input_filename, expected_body_filename, format", 
    [
      ("email_with_html.txt", "email_with_html_plain_text_body.txt", "plain"),
      ("email_with_html.txt", "email_with_html_body.txt", "html")
    ]
  )
  def test_get_email_body(self, input_filename: str, expected_body_filename: str, format: str) -> None:
    email_body = ""
    expected_email_body = ""
    # when
    with open(os.path.join(self.email_examples_path, input_filename), "r") as email_file:
      message = email.message_from_string(email_file.read(), policy=default_policy)
      email_body = self.reader.get_email_body(message, format)
    with open(os.path.join(self.email_examples_path, expected_body_filename), "r") as email_file:
      expected_email_body = email_file.read()
      
    # then
    assert email_body == expected_email_body

  @pytest.mark.parametrize("message, format", 
    [
      ("", "plain"),
      ("", "html"),
      ("abc", "plain"),
      ("abc", "html"),
      (None, "plain"),
      (1, "plain"),
    ]
  )
  def test_get_email_body_raises_an_exception_with_invalid_message(self, message: str, format: str) -> None:
    expected_message = 'Invalid "message" type. Expected type to be email.message.EmailMessage'
    with pytest.raises(AttributeError, match = expected_message):
      self.reader.get_email_body(message, format)

  @pytest.mark.parametrize(
    "input_filename, format", 
    [
      ("email_with_html.txt", ""),
      ("email_with_html.txt", None),
      ("email_with_html.txt", "plainn"),
      ("email_with_html.txt", "Plain"),
      ("email_with_html.txt", "HTML"),
      ("email_with_html.txt", "Html"),
    ]
  )
  def test_get_email_body_raises_an_exception_with_invalid_format(self, input_filename: str, format: any) -> None:

    expected_message = 'Invalid "format". Expected plain or html'
    # when
    with open(os.path.join(self.email_examples_path, input_filename), "r") as email_file:
      message = email.message_from_string(email_file.read(), policy=default_policy)
      with pytest.raises(AttributeError, match = expected_message) as exception:
        _ = self.reader.get_email_body(message, format)
        assert 'Invalid "format". Expected plain or html' in str(exception.value)

  @pytest.mark.parametrize("input_string, expected_output",
    [
      ("2023-02-04T15:26:44.920Z", "04-Feb-2023"),
      ("2023-02-04T15:39:29.058997", "04-Feb-2023"),
      ("2000-01-23T01:23:45.678+09:00", "23-Jan-2000")
    ]
  )
  def test_iso8601_datetime_to_rfc2822_date_string_with_valid_dates(self, input_string: str, expected_output: str) -> None:
    actual_result = self.reader.iso8601_datetime_to_rfc2822_date_string(input_string)
    assert actual_result == expected_output

  @pytest.mark.parametrize("input_string", 
  [
    (""),
    (None),
    (123), # int
    (12.3), # float
    ([1, 2]), # list
    ((2, 3)), # tuple
    (False), # bool
    (True), # bool
    (b'test'), # bytes
    ("2023/02/04 15:26:44")
  ]
  )
  def test_iso8601_datetime_to_rfc2822_date_string_with_invalid_dates_raises_an_exception(self, input_string: str) -> None:
    with pytest.raises(ValueError) as exception:
      _ = self.reader.iso8601_datetime_to_rfc2822_date_string(input_string)
      assert 'Invalid ISO 8601 string' in str(exception.value)

  @pytest.mark.parametrize(
    "response_code, count",
    [
      ('OK', [b'0']),
      ('OK', [b'5']),
    ]
  )
  def test_select_mailbox_and_get_email_count_in_mailbox(self, response_code, count, monkeypatch: MonkeyPatch) -> None:
    class imap4_ssl_mock:
      def select(mailbox, readonly):
        return (response_code, count)
    
    def login_mock(self: IMAP4_SSL):
      return ("OK", [b"test"])

    
    monkeypatch.setattr(IMAPReader, "login", login_mock)
    monkeypatch.setattr("imaplib.IMAP4_SSL", imap4_ssl_mock)
    monkeypatch.setattr(IMAP4_SSL, "open", lambda _: True)


    reader = IMAPReader(email_id="", email_password="", email_host="")
    reader.login()
    reader.imap4_ssl = imap4_ssl_mock
    assert reader.select_mailbox_and_get_email_count_in_mailbox() == (response_code, count)

  @pytest.mark.parametrize("mail_ids, expected_count", 
  [
    ([b'1'], 1),
    ([b'1 2 3 4 5'], 5)
  ])
  def test_fetch_emails(self, mail_ids, expected_count, monkeypatch: MonkeyPatch) -> None:
    class imap4_ssl_mock:
      
      def fetch(mail_id, format='(RFC822)'):
        sample_fetch_response = ('OK', [(b'1 (FLAGS (\\Seen \\Recent) RFC822 {460}', b'Return-Path: <user@test.local>\r\nX-Original-To: user@test.local\r\nDelivered-To: user@test.local\r\nReceived: by user (Postfix, from userid 1000)\r\n\tid 82C7A280DB0; Sun,  5 Feb 2023 05:10:47 -0500 (EST)\r\nDate: Sun, 5 Feb 2023 05:10:47 -0500\r\nFrom: user <user@test.local>\r\nTo: user@test.local\r\nSubject: Test 1\r\nMessage-ID: <Y9+Apzn2XyMvNzpd@test.local>\r\nMIME-Version: 1.0\r\nContent-Type: text/plain; charset=us-ascii\r\nContent-Disposition: inline\r\n\r\nTest 1 email body\r\n'), b')'])
        return sample_fetch_response
    
    monkeypatch.setattr("imaplib.IMAP4_SSL", imap4_ssl_mock)

    reader = IMAPReader(email_id="", email_password="", email_host="")
    reader.imap4_ssl = imap4_ssl_mock
    messages = reader.fetch_emails(mail_ids)

    print(messages[0].get_body().as_string())
    assert len(messages) == expected_count
    assert isinstance(messages[0], email.message.Message)

  @pytest.mark.parametrize("start_date, expected_count", 
  [
    ("2023-02-04T15:26:44.920Z", 5),
  ])
  def test_get_emails_since_emails(self, start_date, expected_count, monkeypatch: MonkeyPatch) -> None:
    class imap4_ssl_mock:
      def select(mailbox, readonly):
        return ("OK", expected_count)
      
      def search(charset, command, parameters):
        search_response = ('OK', [b'1 2 3 4 5'])
        return search_response

      def fetch(mail_id, format='(RFC822)'):
        sample_fetch_response = ('OK', [(b'1 (FLAGS (\\Seen \\Recent) RFC822 {460}', b'Return-Path: <user@test.local>\r\nX-Original-To: user@test.local\r\nDelivered-To: user@test.local\r\nReceived: by user (Postfix, from userid 1000)\r\n\tid 82C7A280DB0; Sun,  5 Feb 2023 05:10:47 -0500 (EST)\r\nDate: Sun, 5 Feb 2023 05:10:47 -0500\r\nFrom: user <user@test.local>\r\nTo: user@test.local\r\nSubject: Test 1\r\nMessage-ID: <Y9+Apzn2XyMvNzpd@test.local>\r\nMIME-Version: 1.0\r\nContent-Type: text/plain; charset=us-ascii\r\nContent-Disposition: inline\r\n\r\nTest 1 email body\r\n'), b')'])
        return sample_fetch_response
    
    monkeypatch.setattr("imaplib.IMAP4_SSL", imap4_ssl_mock)

    reader = IMAPReader(email_id="", email_password="", email_host="")
    reader.imap4_ssl = imap4_ssl_mock
    messages = reader.get_emails_since_date(start_date)

    assert isinstance(messages, list)
    assert len(messages) == expected_count
    assert isinstance(messages[0], email.message.Message)


  @pytest.mark.parametrize("expected_count", 
  [
    (5),
  ])
  def test_get_mail(self, expected_count, monkeypatch: MonkeyPatch) -> None:
    class imap4_ssl_mock:
      def select(mailbox, readonly):
        return ("OK", expected_count)
      
      def search(charset, command):
        search_response = ('OK', [b'1 2 3 4 5'])
        return search_response

      def fetch(mail_id, format='(RFC822)'):
        sample_fetch_response = ('OK', [(b'1 (FLAGS (\\Seen \\Recent) RFC822 {460}', b'Return-Path: <user@test.local>\r\nX-Original-To: user@test.local\r\nDelivered-To: user@test.local\r\nReceived: by user (Postfix, from userid 1000)\r\n\tid 82C7A280DB0; Sun,  5 Feb 2023 05:10:47 -0500 (EST)\r\nDate: Sun, 5 Feb 2023 05:10:47 -0500\r\nFrom: user <user@test.local>\r\nTo: user@test.local\r\nSubject: Test 1\r\nMessage-ID: <Y9+Apzn2XyMvNzpd@test.local>\r\nMIME-Version: 1.0\r\nContent-Type: text/plain; charset=us-ascii\r\nContent-Disposition: inline\r\n\r\nTest 1 email body\r\n'), b')'])
        return sample_fetch_response
    
    monkeypatch.setattr("imaplib.IMAP4_SSL", imap4_ssl_mock)

    reader = IMAPReader(email_id="", email_password="", email_host="")
    reader.imap4_ssl = imap4_ssl_mock
    messages = reader.get_mail()

    assert isinstance(messages, list)
    assert len(messages) == expected_count
    assert isinstance(messages[0], email.message.Message)

  @pytest.mark.parametrize("search_string, expected_count", 
  [
    ("Test", 5),
    ("some long search string that should return no results", 0)
  ])
  def test_get_emails_with_subject(self, search_string, expected_count, monkeypatch: MonkeyPatch) -> None:
    class imap4_ssl_mock:
      def select(mailbox, readonly):
        return ("OK", expected_count)
      
      def search(charset, command, parameters):
        search_response = ('OK', [b'1 2 3 4 5'])
        search_response_no_results = ('OK', [b''])
        return search_response if expected_count > 0 else search_response_no_results

      def fetch(mail_id, format='(RFC822)'):
        sample_fetch_response = ('OK', [(b'1 (FLAGS (\\Seen \\Recent) RFC822 {460}', b'Return-Path: <user@test.local>\r\nX-Original-To: user@test.local\r\nDelivered-To: user@test.local\r\nReceived: by user (Postfix, from userid 1000)\r\n\tid 82C7A280DB0; Sun,  5 Feb 2023 05:10:47 -0500 (EST)\r\nDate: Sun, 5 Feb 2023 05:10:47 -0500\r\nFrom: user <user@test.local>\r\nTo: user@test.local\r\nSubject: Test 1\r\nMessage-ID: <Y9+Apzn2XyMvNzpd@test.local>\r\nMIME-Version: 1.0\r\nContent-Type: text/plain; charset=us-ascii\r\nContent-Disposition: inline\r\n\r\nTest 1 email body\r\n'), b')'])
        return sample_fetch_response
    
    monkeypatch.setattr("imaplib.IMAP4_SSL", imap4_ssl_mock)

    reader = IMAPReader(email_id="", email_password="", email_host="")
    reader.imap4_ssl = imap4_ssl_mock
    messages = reader.get_emails_with_subject(search_string)

    assert isinstance(messages, list)
    assert len(messages) == expected_count
    if expected_count > 0:
      assert isinstance(messages[0], email.message.Message)
  
  @pytest.mark.parametrize("search_string, expected_count", 
  [
    ("Test", 5),
    ("some long search string that should return no results", 0)
  ])
  def test_get_emails_with_body(self, search_string, expected_count, monkeypatch: MonkeyPatch) -> None:
    class imap4_ssl_mock:
      def select(mailbox, readonly):
        return ("OK", expected_count)
      
      def search(charset, command, parameters):
        search_response = ('OK', [b'1 2 3 4 5'])
        search_response_no_results = ('OK', [b''])
        return search_response if expected_count > 0 else search_response_no_results

      def fetch(mail_id, format='(RFC822)'):
        sample_fetch_response = ('OK', [(b'1 (FLAGS (\\Seen \\Recent) RFC822 {460}', b'Return-Path: <user@test.local>\r\nX-Original-To: user@test.local\r\nDelivered-To: user@test.local\r\nReceived: by user (Postfix, from userid 1000)\r\n\tid 82C7A280DB0; Sun,  5 Feb 2023 05:10:47 -0500 (EST)\r\nDate: Sun, 5 Feb 2023 05:10:47 -0500\r\nFrom: user <user@test.local>\r\nTo: user@test.local\r\nSubject: Test 1\r\nMessage-ID: <Y9+Apzn2XyMvNzpd@test.local>\r\nMIME-Version: 1.0\r\nContent-Type: text/plain; charset=us-ascii\r\nContent-Disposition: inline\r\n\r\nTest 1 email body\r\n'), b')'])
        return sample_fetch_response
    
    monkeypatch.setattr("imaplib.IMAP4_SSL", imap4_ssl_mock)

    reader = IMAPReader(email_id="", email_password="", email_host="")
    reader.imap4_ssl = imap4_ssl_mock
    messages = reader.get_emails_with_body(search_string)

    assert isinstance(messages, list)
    assert len(messages) == expected_count
    if expected_count > 0:
      assert isinstance(messages[0], email.message.Message)