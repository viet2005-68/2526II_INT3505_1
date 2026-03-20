# openapi_client.DefaultApi

All URIs are relative to *http://localhost:4001*

Method | HTTP request | Description
------------- | ------------- | -------------
[**books_get**](DefaultApi.md#books_get) | **GET** /books | Get all books
[**books_id_get**](DefaultApi.md#books_id_get) | **GET** /books/{id} | Get book by ID


# **books_get**
> List[Book] books_get()

Get all books

### Example


```python
import openapi_client
from openapi_client.models.book import Book
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:4001
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost:4001"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)

    try:
        # Get all books
        api_response = api_instance.books_get()
        print("The response of DefaultApi->books_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->books_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**List[Book]**](Book.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **books_id_get**
> Book books_id_get(id)

Get book by ID

### Example


```python
import openapi_client
from openapi_client.models.book import Book
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:4001
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost:4001"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)
    id = 56 # int | 

    try:
        # Get book by ID
        api_response = api_instance.books_id_get(id)
        print("The response of DefaultApi->books_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->books_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 

### Return type

[**Book**](Book.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**404** | Not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

