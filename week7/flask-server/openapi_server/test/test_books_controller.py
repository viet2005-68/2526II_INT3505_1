import unittest

from flask import json

from openapi_server.models.book import Book  # noqa: E501
from openapi_server.models.create_book_payload import CreateBookPayload  # noqa: E501
from openapi_server.models.error import Error  # noqa: E501
from openapi_server.models.paginated_books_response import PaginatedBooksResponse  # noqa: E501
from openapi_server.models.update_book_payload import UpdateBookPayload  # noqa: E501
from openapi_server.test import BaseTestCase


class TestBooksController(BaseTestCase):
    """BooksController integration test stubs"""

    def test_api_books_book_id_delete(self):
        """Test case for api_books_book_id_delete

        Delete a book
        """
        headers = { 
            'Accept': 'application/json',
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/api/books/{book_id}'.format(book_id=56),
            method='DELETE',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_api_books_book_id_get(self):
        """Test case for api_books_book_id_get

        Get a book by ID
        """
        headers = { 
            'Accept': 'application/json',
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/api/books/{book_id}'.format(book_id=56),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_api_books_book_id_put(self):
        """Test case for api_books_book_id_put

        Update a book
        """
        update_book_payload = {"year":1925,"author":"F. Scott Fitzgerald","title":"The Great Gatsby"}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/api/books/{book_id}'.format(book_id=56),
            method='PUT',
            headers=headers,
            data=json.dumps(update_book_payload),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_api_books_get(self):
        """Test case for api_books_get

        Get all books with pagination and search
        """
        query_string = [('page', 1),
                        ('limit', 10),
                        ('search', '')]
        headers = { 
            'Accept': 'application/json',
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/api/books',
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_api_books_post(self):
        """Test case for api_books_post

        Create a new book
        """
        create_book_payload = {"year":1925,"author":"F. Scott Fitzgerald","title":"The Great Gatsby"}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/api/books',
            method='POST',
            headers=headers,
            data=json.dumps(create_book_payload),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
