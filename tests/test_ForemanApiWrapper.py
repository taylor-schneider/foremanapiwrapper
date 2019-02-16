from unittest import TestCase
from ForemanApiWrapper import ForemanApiWrapper


class Test_ForemanApiWrapper(TestCase):

    def __init__(self, *args, **kwargs):
        super(self).__init__(*args, **kwargs)
        self.username = "admin"
        self.password = "password"
        self.url = "https://15.4.7.1"
        self.verifySsl = False

    def test_MakeApiCall_Success(self):

        api = ForemanApiWrapper(self.username, self.password, self.url, self.verifySsl)

        endpoint = "/api/environments"
        method = "get"

        api.make_api_call(endpoint, method)

    def test_MakeApiCall_Failure_InvalidCredentials(self):

        username = "fake_user"
        password = "fake_password"

        api = ForemanApiWrapper(username, password, self.url, self.verifySsl)

        endpoint = "/api/environments"
        method = "get"

        with self.assertRaises(Exception) as e:
            api.make_api_call(endpoint, method)

        expected_error = 'Unable to authenticate user {0}'.format(username)
        self.assertEqual(expected_error, e.exception.args[0])

    def test_MakeApiCall_Success_CreateEnvironment(self):

        api = ForemanApiWrapper(self.username, self.password, self.url, self.verifySsl)

        endpoint = "/api/environments"
        method = "post"
        arguments =  {
            "environment": {
                "name": "some_environment"
            }
        }

        response = api.make_api_call(endpoint, method, arguments)
        self.assertTrue("created_at" in response.keys())
