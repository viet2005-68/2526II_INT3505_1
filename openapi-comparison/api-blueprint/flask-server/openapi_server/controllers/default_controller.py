import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.create_a_new_book201_response import CreateANewBook201Response  # noqa: E501
from openapi_server.models.create_a_new_book400_response import CreateANewBook400Response  # noqa: E501
from openapi_server.models.create_a_new_book_request import CreateANewBookRequest  # noqa: E501
from openapi_server.models.delete_a_book200_response import DeleteABook200Response  # noqa: E501
from openapi_server.models.get_all_books200_response_inner import GetAllBooks200ResponseInner  # noqa: E501
from openapi_server.models.get_book_by_id200_response import GetBookByID200Response  # noqa: E501
from openapi_server.models.get_book_by_id404_response import GetBookByID404Response  # noqa: E501
from openapi_server.models.update_a_book200_response import UpdateABook200Response  # noqa: E501
from openapi_server.models.update_a_book_request import UpdateABookRequest  # noqa: E501
from openapi_server import util


def create_a_new_book(body=None):  # noqa: E501
    """Create a new book

     # noqa: E501

    :param create_a_new_book_request: 
    :type create_a_new_book_request: dict | bytes

    :rtype: Union[CreateANewBook201Response, Tuple[CreateANewBook201Response, int], Tuple[CreateANewBook201Response, int, Dict[str, str]]
    """
    create_a_new_book_request = body
    if connexion.request.is_json:
        create_a_new_book_request = CreateANewBookRequest.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def delete_a_book(id):  # noqa: E501
    """Delete a book

     # noqa: E501

    :param id: ID của book
    :type id: int

    :rtype: Union[DeleteABook200Response, Tuple[DeleteABook200Response, int], Tuple[DeleteABook200Response, int, Dict[str, str]]
    """
    return 'do some magic!'


def get_all_books():  # noqa: E501
    """Get all books

     # noqa: E501


    :rtype: Union[List[GetAllBooks200ResponseInner], Tuple[List[GetAllBooks200ResponseInner], int], Tuple[List[GetAllBooks200ResponseInner], int, Dict[str, str]]
    """
    return 'do some magic!'


def get_book_by_id(id):  # noqa: E501
    """Get book by ID

     # noqa: E501

    :param id: ID của book
    :type id: int

    :rtype: Union[GetBookByID200Response, Tuple[GetBookByID200Response, int], Tuple[GetBookByID200Response, int, Dict[str, str]]
    """
    return 'do some magic!'


def update_a_book(id, body=None):  # noqa: E501
    """Update a book

     # noqa: E501

    :param id: ID của book
    :type id: int
    :param update_a_book_request: 
    :type update_a_book_request: dict | bytes

    :rtype: Union[UpdateABook200Response, Tuple[UpdateABook200Response, int], Tuple[UpdateABook200Response, int, Dict[str, str]]
    """
    update_a_book_request = body
    if connexion.request.is_json:
        update_a_book_request = UpdateABookRequest.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
