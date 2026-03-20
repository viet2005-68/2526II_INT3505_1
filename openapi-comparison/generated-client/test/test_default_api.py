# coding: utf-8
"""
Test cho Library API sử dụng openapi_client được sinh từ OpenAPI spec.
Cần server đang chạy tại http://localhost:4001
Chạy: python test/test_default_api.py
"""

import unittest
import openapi_client
from openapi_client.api.default_api import DefaultApi


class TestDefaultApi(unittest.TestCase):
    """Test DefaultApi gọi thật vào server"""

    def setUp(self):
        config = openapi_client.Configuration(host="http://localhost:4001")
        client = openapi_client.ApiClient(configuration=config)
        self.api = DefaultApi(api_client=client)

    def test_books_get(self):
        """GET /books -> trả về list"""
        result = self.api.books_get()
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        print(f"  [PASS] GET /books -> {len(result)} books")

    def test_books_id_get_found(self):
        """GET /books/1 -> trả về book"""
        result = self.api.books_id_get(1)
        self.assertEqual(result.id, 1)
        print(f"  [PASS] GET /books/1 -> title={result.title}")

    def test_books_id_get_not_found(self):
        """GET /books/9999 -> 404"""
        from openapi_client.exceptions import ApiException
        with self.assertRaises(ApiException) as ctx:
            self.api.books_id_get(9999)
        self.assertEqual(ctx.exception.status, 404)
        print(f"  [PASS] GET /books/9999 -> 404 Not Found")


if __name__ == '__main__':
    unittest.main(verbosity=2)
