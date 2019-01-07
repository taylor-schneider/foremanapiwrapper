import requests
from requests.auth import HTTPBasicAuth
import json

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
            raise Exception(ForemanApiWrapper.ErrorMessage_ApiCall) from e



