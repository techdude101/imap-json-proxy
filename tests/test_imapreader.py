import unittest
import os
import email
import pytest
from src.flaskapp.imapreader import IMAPReader
from email.policy import default as default_policy

class TestImapReader(object):
  reader = IMAPReader()

  email_examples_path = os.path.join(os.getcwd(), "email_examples")
  
  @pytest.mark.parametrize(
    "input_filename, expected_body_filename, format", 
    [
      ("email_with_html.txt", "email_with_html_plain_text_body.txt", "plain"),
      ("email_with_html.txt", "email_with_html_body.txt", "html")
    ]
  )
  def test_get_email_body(self, input_filename, expected_body_filename, format):
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
      ("abc", "html")
    ]
  )
  def test_get_email_body_raises_an_exception_with_invalid_message(self, message, format):
    with pytest.raises(AttributeError) as exception:
      self.reader.get_email_body(message, format)
      assert 'Invalid "message" type. Expected type to be email.message.EmailMessage' in str(exception.value)

  @pytest.mark.parametrize(
    "input_filename, format", 
    [
      ("email_with_html.txt", ""),
      # ("email_with_html.txt", None),
      # ("email_with_html.txt", "plainn"),
      # ("email_with_html.txt", "Plain"),
      # ("email_with_html.txt", "HTML"),
      # ("email_with_html.txt", "html"),
    ]
  )
  def test_get_email_body_raises_an_exception_with_invalid_format(self, input_filename, format):
    email_body = ""
    expected_email_body = ""
    # when
    with open(os.path.join(self.email_examples_path, input_filename), "r") as email_file:
      message = email.message_from_string(email_file.read(), policy=default_policy)
      with pytest.raises(AttributeError) as exception:
        email_body = self.reader.get_email_body(message, format)
        assert 'Invalid "format". Expected plain or html' in str(exception.value)