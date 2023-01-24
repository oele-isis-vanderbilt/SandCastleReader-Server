# Built-in Imports
import json
import logging
import datetime

# Third-party Imports
import pytest

# Internal Imports
from scrs.app import app

# Setting Up Logger
logger = logging.getLogger()


@pytest.fixture
def client():
    yield app.test_client()


def login(client, username, password):
    return client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=True,
    )


def logout(client, username):
    return client.post("/logout", data={"username": username}, follow_redirects=True)


def send_entry(client, timestamp, topic, information):
    return client.post(
        "/logs",
        data={"timestamp": timestamp, "topic": topic, "information": information},
        follow_redirects=True,
    )


def test_ping(client):
    response = client.get("/ping", content_type="html/text")
    assert response.status_code == 200
    assert json.loads(response.data)["response"] == "pong"


def test_login_wrong_username_and_password(client):
    assert not json.loads(login(client, "", "").data)["success"]


def test_login_correct_username_and_password(client):
    response = json.loads(login(client, "test_user", "123456789").data)
    logger.debug(response)
    assert response["success"]


def test_login_and_creating_record(client):
    login(client, "test_user", "123456789")
    response = json.loads(
        send_entry(client, datetime.datetime.now(), "init", "Hello World").data
    )
    assert response["success"]


def test_login_and_logout(client):
    login(client, "test_user", "123456789")
    response = json.loads(logout(client, "test_user").data)
    assert response["success"] and response["username"] == "test_user"
