import requests
from requests.auth import HTTPBasicAuth
import json

from ForemanApiWrapper.ForemanApiWrapper.ForemanApiCallException import ForemanApiCallException

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

            if hasattr(results, "_content"):
                jsonString = results.content.decode("utf-8")
                obj = json.loads(jsonString)
                error = obj['error']

                msg = None
                if "full_messages" in error.keys():
                    msg = error["full_messages"][0]
                if "message" in error.keys():
                    msg = error["message"]
                if msg:
                    raise ForemanApiCallException(
                        msg,
                        endpoint,
                        method,
                        results,
                        arguments,
                        headers) from e

                raise ForemanApiCallException(
                    ForemanApiWrapper.ErrorMessage_ApiCall,
                    endpoint,
                    method,
                    results,
                    arguments,
                    headers) from e



