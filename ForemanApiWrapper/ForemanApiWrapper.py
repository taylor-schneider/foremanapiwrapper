import requests
from requests.auth import HTTPBasicAuth
import json
import logging

from ForemanApiWrapper.ForemanApiWrapper.ForemanApiCallException import ForemanApiCallException

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

class ForemanApiWrapper():

    ErrorMessage_ApiCall = "An error occurred while making an API call."

    def __init__(self, username, password, url, verifySsl):
        self.Username = username
        self.Password = password
        self.Auth = HTTPBasicAuth(username , password)
        self.Url = url
        self.VerifySsl = verifySsl

    def MakeApiCall(self, endpoint, method, arguments=None, headers=None):

        try:
            # Make the api call
            m = str.lower(method)
            func = getattr(requests, m)
            url = self.Url + endpoint

            logger.debug("Making api call [{0}] {1}".format(method.upper(), url))
            if arguments:
                logger.debug("Json body:")
                prettyJson = json.dumps(arguments, sort_keys=True, indent=4)
                for line in prettyJson.split("\n"):
                    logger.debug(line)

            results = None
            if arguments:
                results = func(url, auth=self.Auth, verify=self.VerifySsl, json=arguments, headers=headers)
            else:
                results = func(url, auth=self.Auth, verify=self.VerifySsl)

            # Raise an exception if we did not get a 200 response
            results.raise_for_status()

            # Convert the response to an object
            jsonString = results.content.decode("utf-8")
            obj = json.loads(jsonString)

            return obj
        except Exception as e:

            # An exception can be raised in several ways
            # In some cases, a non 200 response may return a result object
            # The result may contain json representation of an error

            msg = None
            try:
                jsonString = results.content.decode("utf-8")
                resultObj = json.loads(jsonString)
                error = resultObj['error']
                if "full_messages" in error.keys():
                    msg = error["full_messages"][0]
                if "message" in error.keys():
                    msg = error["message"]
            except:
                pass

            if msg:
                raise ForemanApiCallException(
                    msg,
                    endpoint,
                    method,
                    results,
                    arguments,
                    headers) from e

            # If we got here, the api did not return a json error
            raise ForemanApiCallException(
                ForemanApiWrapper.ErrorMessage_ApiCall,
                endpoint,
                method,
                results,
                arguments,
                headers) from e

    @staticmethod
    def _GetHeadersForHttpMethod(httpMethod):

        # Foreman's API specifies that put and post api calls must set the Content-type header
        # If we dont, we will get an exception as follows:
        #       Exception.args[0]:
        #           '415 Client Error: Unsupported Media Type for url: https://15.4.7.1/api/environments'
        #
        #       response._content:
        #           b'{\n  "error": {"message":"\'Content-Type: \' is unsupported in API v2 for POST and PUT requests. Please use \'Content-Type: application/json\'."}\n}\n'

        headers = {}
        if httpMethod.lower() in ["put", "post"]:
            headers = {'Content-type': 'application/json', "charset": "utf-8"}

        return headers
