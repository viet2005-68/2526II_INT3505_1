import unittest

from flask import json

from openapi_server.models.error import Error  # noqa: E501
from openapi_server.models.login_payload import LoginPayload  # noqa: E501
from openapi_server.models.login_response import LoginResponse  # noqa: E501
from openapi_server.models.message_response import MessageResponse  # noqa: E501
from openapi_server.models.register_payload import RegisterPayload  # noqa: E501
from openapi_server.test import BaseTestCase


class TestAuthController(BaseTestCase):
    """AuthController integration test stubs"""

    def test_api_auth_login_post(self):
        """Test case for api_auth_login_post

        Login and get Bearer token
        """
        login_payload = {"password":"Str0ngPass","username":"alice"}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/api/auth/login',
            method='POST',
            headers=headers,
            data=json.dumps(login_payload),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_api_auth_register_post(self):
        """Test case for api_auth_register_post

        Register a new user
        """
        register_payload = {"password":"Str0ngPass","username":"alice"}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/api/auth/register',
            method='POST',
            headers=headers,
            data=json.dumps(register_payload),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
