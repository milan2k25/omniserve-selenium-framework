import json
import requests
from typing import Any
 
 
def get_api_response(url: str, method: str, headers: dict, body: Any,
                     expected_status_code: int=200):
    """Send a HTTP API request and returns the response as JSON
    If the request fails, sends the error or response text
 
    Args:
        url (str): URI to send the request to
        method (str): HTTP method for the request
        headers (dict): HTTP headers ro use for the request
        body (Any): json payload to send, if any
        expected_status_code (int, optional): Expected status code to assume success. Defaults to 200.
 
    Raises:
        NotImplementedError: when the method is not supported
 
    Returns:
        [tuple]: A boolean indicating success, and the response (or failure reason)
    """
    # Convert to lower case to help in easy comparison
    method = method.lower()
    try:
        if method == 'get':
            r = requests.get(url, headers=headers)
        elif method == 'post':
            r = requests.post(url, headers=headers, data=json.dumps(body))
        elif method == 'put':
            r = requests.put(url, headers=headers, data=json.dumps(body))
        elif method == 'delete':
            r = requests.delete(url, headers=headers)
        else:
            raise NotImplementedError(f"Method {method} not supported")
        r.raise_for_status()
        if r.status_code == expected_status_code:
            return True, r.json()
        return False, r.text()
    except requests.ConnectionError:
        return False, "Failed to connect to url " + url
    except requests.HTTPError:
        return False, "HTTP error when connecting to " + url
    except requests.Timeout:
        return False, "Timed out when connecting to " + url