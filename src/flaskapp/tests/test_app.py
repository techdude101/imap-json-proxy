import os
import email
import pytest
import json
from schema import Schema, And
from email.policy import default as default_policy
from fastapi.testclient import TestClient
from pytest import MonkeyPatch
from http import HTTPStatus

import importlib

from imapreader import IMAPReader
from app import app


class TestApp(object):

  client = TestClient(app)
  json_response_schema = Schema({
    "to": And(str),
    "from": And(str),
    "subject": And(str),
    "date": And(str),
    "body": And(str),
  })

  bad_request_schema = Schema({
    "detail": And(str)
  })

  
  def test_read_index(self):
      response = self.client.get("/")
      assert response.status_code == HTTPStatus.OK
      assert response.json() == {"version": "1.0.0"}


  def test_get_all_messages_returns_no_messages(self, monkeypatch: MonkeyPatch):
      def mock_login(self):
          return None

      def mock_close(self):
          return None

      def mock_get_mail(self):
        return []

      monkeypatch.setattr(IMAPReader, "login", mock_login)
      monkeypatch.setattr(IMAPReader, "close", mock_close)

      monkeypatch.setattr(IMAPReader, "get_mail", mock_get_mail)
      response = self.client.get("/messages/all")

      assert response.status_code == HTTPStatus.OK
      assert response.json() == []

  @pytest.mark.parametrize(
    "input_filename", 
    [
      ("email_with_html.txt")
    ]
  )
  def test_get_all_messages_single_message_in_mailbox(self, monkeypatch: MonkeyPatch, input_filename):
      def read_messages_from_file(input_filename):
        email_examples_path = os.path.join(os.getcwd(), "..", "email_examples")
        messages = []
        with open(os.path.join(email_examples_path, input_filename), "r") as email_file:
          message = email.message_from_string(email_file.read(), policy=default_policy)
          messages.append(message)
        return messages

      def mock_login(self):
          return None

      def mock_close(self):
          return None

      def mock_get_mail(self):
        return read_messages_from_file(input_filename)

      monkeypatch.setattr(IMAPReader, "login", mock_login)
      monkeypatch.setattr(IMAPReader, "close", mock_close)

      monkeypatch.setattr(IMAPReader, "get_mail", mock_get_mail)
      response = self.client.get("/messages/all")

      json_response = response.json()
      assert response.status_code == HTTPStatus.OK
      assert isinstance(json_response, list)
      assert len(json_response) == 1
      assert self.json_response_schema.is_valid(json_response[0]) == True

  @pytest.mark.parametrize(
    "input_filename", 
    [
      ("email_with_html.txt")
    ]
  )
  def test_get_latest_message_single_message_in_mailbox(self, monkeypatch: MonkeyPatch, input_filename):
      def read_messages_from_file(input_filename):
        email_examples_path = os.path.join(os.getcwd(), "..", "email_examples")
        messages = []
        with open(os.path.join(email_examples_path, input_filename), "r") as email_file:
          message = email.message_from_string(email_file.read(), policy=default_policy)
          messages.append(message)
        return messages

      def mock_login(self):
          return None

      def mock_close(self):
          return None

      def mock_get_mail(self):
        return read_messages_from_file(input_filename)

      monkeypatch.setattr(IMAPReader, "login", mock_login)
      monkeypatch.setattr(IMAPReader, "close", mock_close)

      monkeypatch.setattr(IMAPReader, "get_mail", mock_get_mail)
      response = self.client.get("/messages/latest")

      json_response = response.json()
      assert response.status_code == HTTPStatus.OK
      assert isinstance(json_response, dict)
      assert self.json_response_schema.is_valid(json_response) == True


  @pytest.mark.parametrize(
    "input_filenames, number_of_messages", 
    [
      (["email_with_html.txt"], 0),
      (["email_with_html.txt"], 1),
      (["email_with_html.txt", "email_test_1_plain.txt"], 2)
    ]
  )
  def test_get_last_n_messages(self, monkeypatch: MonkeyPatch, input_filenames, number_of_messages):
      def read_messages_from_file(input_filenames):
        email_examples_path = os.path.join(os.getcwd(), "..", "email_examples")
        messages = []
        for input_filename in input_filenames:
          with open(os.path.join(email_examples_path, input_filename), "r") as email_file:
            message = email.message_from_string(email_file.read(), policy=default_policy)
            messages.append(message)
        return messages

      def mock_login(self):
          return None

      def mock_close(self):
          return None

      def mock_get_mail(self):
        return read_messages_from_file(input_filenames)

      monkeypatch.setattr(IMAPReader, "login", mock_login)
      monkeypatch.setattr(IMAPReader, "close", mock_close)

      monkeypatch.setattr(IMAPReader, "get_mail", mock_get_mail)
      response = self.client.get(f"/messages/last?count={number_of_messages}")

      json_response = response.json()
      assert response.status_code == HTTPStatus.OK
      assert isinstance(json_response, list)
      assert len(json_response) == number_of_messages
      if number_of_messages > 0:
        assert self.json_response_schema.is_valid(json_response[0]) == True


  @pytest.mark.parametrize(
    "input_filenames, number_of_messages", 
    [
      (["email_with_html.txt"], "null"),
      (["email_with_html.txt"], None),
    ]
  )
  def test_get_last_message_invalid_count(self, monkeypatch: MonkeyPatch, input_filenames, number_of_messages):
      def read_messages_from_file(input_filenames):
        email_examples_path = os.path.join(os.getcwd(), "..", "email_examples")
        messages = []
        for input_filename in input_filenames:
          with open(os.path.join(email_examples_path, input_filename), "r") as email_file:
            message = email.message_from_string(email_file.read(), policy=default_policy)
            messages.append(message)
        return messages

      def mock_login(self):
          return None

      def mock_close(self):
          return None

      def mock_get_mail(self):
        return read_messages_from_file(input_filenames)

      monkeypatch.setattr(IMAPReader, "login", mock_login)
      monkeypatch.setattr(IMAPReader, "close", mock_close)

      monkeypatch.setattr(IMAPReader, "get_mail", mock_get_mail)
      response = self.client.get(f"/messages/last?count={number_of_messages}")

      assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

  def test_search_by_no_params(self, monkeypatch: MonkeyPatch):
      def mock_login(self):
          return None

      def mock_close(self):
          return None

      monkeypatch.setattr(IMAPReader, "login", mock_login)
      monkeypatch.setattr(IMAPReader, "close", mock_close)

      response = self.client.get(f"/messages/search")

      assert response.status_code == HTTPStatus.BAD_REQUEST
      assert self.bad_request_schema.is_valid(response.json()) == True


  @pytest.mark.parametrize(
    "query_params",
    [
        ("body=test&subject=test"),
        ("body=test&subject=test&datetime=123"),
    ]
  )
  def test_search_by_too_many_params(self, monkeypatch: MonkeyPatch, query_params):
      def mock_login(self):
          return None

      def mock_close(self):
          return None

      monkeypatch.setattr(IMAPReader, "login", mock_login)
      monkeypatch.setattr(IMAPReader, "close", mock_close)

      response = self.client.get(f"/messages/search?{query_params}")

      assert response.status_code == HTTPStatus.BAD_REQUEST
      assert self.bad_request_schema.is_valid(response.json()) == True