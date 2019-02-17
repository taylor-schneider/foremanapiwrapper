import requests
import json
import logging
import sys
from requests.auth import HTTPBasicAuth
from ForemanApiCallException import ForemanApiCallException


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


PY3 = sys.version_info >= (3, 0)


class ForemanApiWrapper:

    ErrorMessage_ApiCall = "An error occurred while making an API call."

    def __init__(self, username, password, url, verify_ssl):
        self.username = username
        self.password = password
        self.auth = HTTPBasicAuth(username, password)
        self.url = url
        self.verify_ssl = verify_ssl

    def make_api_call(self, endpoint, method, arguments=None, headers=None):

        results = None
        try:
            method_name = str.lower(method)
            function_pointer = getattr(requests, method_name)
            request_url = self.url + endpoint

            logger.debug("Making api call [{0}] {1}".format(method.upper(), request_url))

            if arguments:
                logger.debug("Json body:")
                pretty_json = json.dumps(arguments, sort_keys=True, indent=4)
                for line in pretty_json.split("\n"):
                    logger.debug(line)

            results = None
            if arguments:
                results = function_pointer(request_url, auth=self.auth, verify=self.verify_ssl, json=arguments, headers=headers)
            else:
                results = function_pointer(request_url, auth=self.auth, verify=self.verify_ssl)

            # Raise an exception if we did not get a 200 response
            results.raise_for_status()

            # Convert the response to an object
            json_string = results.content.decode("utf-8")
            obj = json.loads(json_string)

            return obj
        except Exception as e:

            # An exception can be raised in several ways
            # In some cases, a non 200 response may return a result object
            # The result may contain json representation of an error

            msg = None
            try:
                json_string = results.content.decode("utf-8")
                result_obj = json.loads(json_string)
                error = result_obj['error']
                if "full_messages" in error.keys():
                    msg = error["full_messages"][0]
                if "message" in error.keys():
                    msg = error["message"]
            except:
                pass

            if not msg:
                msg = ForemanApiWrapper.ErrorMessage_ApiCall

            ex = ForemanApiCallException(
                    msg,
                    endpoint,
                    method,
                    results,
                    arguments,
                    headers)

            if PY3:
                raise ex from e
            else:
                from future.utils import raise_from
                raise_from(ex, e)

    @staticmethod
    def _get_headers_for_http_method(http_method):

        # Foreman's API specifies that put and post api calls must set the Content-type header
        # If we dont, we will get an exception as follows:
        #       Exception.args[0]:
        #           '415 Client Error: Unsupported Media Type for url: https://15.4.7.1/api/environments'
        #
        #       response._content:
        #           b'{\n  "error": {"message":"\'Content-Type: \' is unsupported in API v2 for POST and PUT requests. Please use \'Content-Type: application/json\'."}\n}\n'

        headers = {}
        if http_method.lower() in ["put", "post"]:
            headers = {'Content-type': 'application/json', "charset": "utf-8"}

        return headers
