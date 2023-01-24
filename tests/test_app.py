# Built-in Imports
import json
import logging

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
        data={'username': username, 'password': password},
        follow_redirects=True
    )

def test_ping(client):
    response = client.get("/ping", content_type="html/text")
    assert response.status_code == 200
    assert json.loads(response.data) == {'response': 'pong'}

def test_login_wrong_username_and_password(client):
    assert json.loads(login(client, '', '').data) == {'success': False}

def test_login_correct_username_and_password(client):
    response = json.loads(login(client, 'test_user', '123456789').data)
    logger.debug(response)
    assert response['success'] == True
