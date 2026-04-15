import unittest

from flask import json

from openapi_server.models.create_a_new_book201_response import CreateANewBook201Response  # noqa: E501
from openapi_server.models.create_a_new_book400_response import CreateANewBook400Response  # noqa: E501
from openapi_server.models.create_a_new_book_request import CreateANewBookRequest  # noqa: E501
from openapi_server.models.delete_a_book200_response import DeleteABook200Response  # noqa: E501
from openapi_server.models.get_all_books200_response_inner import GetAllBooks200ResponseInner  # noqa: E501
from openapi_server.models.get_book_by_id200_response import GetBookByID200Response  # noqa: E501
from openapi_server.models.get_book_by_id404_response import GetBookByID404Response  # noqa: E501
from openapi_server.models.update_a_book200_response import UpdateABook200Response  # noqa: E501
from openapi_server.models.update_a_book_request import UpdateABookRequest  # noqa: E501
from openapi_server.test import BaseTestCase


class TestDefaultController(BaseTestCase):
    """DefaultController integration test stubs"""

    def test_create_a_new_book(self):
        """Test case for create_a_new_book

        Create a new book
        """
        create_a_new_book_request = openapi_server.CreateANewBookRequest()
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/books',
            method='POST',
            headers=headers,
            data=json.dumps(create_a_new_book_request),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_a_book(self):
        """Test case for delete_a_book

        Delete a book
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/books/{id}'.format(id=56),
            method='DELETE',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_all_books(self):
        """Test case for get_all_books

        Get all books
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/books',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_book_by_id(self):
        """Test case for get_book_by_id

        Get book by ID
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/books/{id}'.format(id=56),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_update_a_book(self):
        """Test case for update_a_book

        Update a book
        """
        update_a_book_request = openapi_server.UpdateABookRequest()
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/books/{id}'.format(id=56),
            method='PUT',
            headers=headers,
            data=json.dumps(update_a_book_request),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
