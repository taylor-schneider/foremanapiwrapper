from unittest import TestCase
from ForemanApiWrapper import ForemanApiWrapper


class Test_ForemanApiWrapper(TestCase):

    def __init__(self, *args, **kwargs):
        super(Test_ForemanApiWrapper, self).__init__(*args, **kwargs)
        self.username = "admin"
        self.password = "password"
        self.url = "https://15.4.7.1"
        self.verifySsl = False

    def test_make_api_call_success(self):

        api = ForemanApiWrapper(self.username, self.password, self.url, self.verifySsl)

        endpoint = "/api/environments"
        method = "get"

        api.make_api_call(endpoint, method)

    def test_make_api_call_failure_invalid_credentials(self):

        username = "fake_user"
        password = "fake_password"

        api = ForemanApiWrapper(username, password, self.url, self.verifySsl)

        endpoint = "/api/environments"
        method = "get"

        with self.assertRaises(Exception) as e:
            api.make_api_call(endpoint, method)

        expected_error = 'Unable to authenticate user {0}'.format(username)
        self.assertEqual(expected_error, e.exception.args[0])

    def test_make_api_call_success_create_environment(self):

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
