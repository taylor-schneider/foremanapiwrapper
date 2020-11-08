import logging
from unittest import TestCase
from ForemanApiWrapper.ForemanApiUtilities.ForemanApiWrapper import ForemanApiWrapper
from ForemanApiWrapper.RecordUtilities import RecordComparison

# Configure logging format and level
logFormat = '%(asctime)s,%(msecs)d %(levelname)-8s [%(module)s:%(funcName)s():%(lineno)d] %(message)s'

logging.basicConfig(format=logFormat,
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.DEBUG)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

class Test_ForemanApiWrapper(TestCase):

    def __init__(self, *args, **kwargs):
        super(Test_ForemanApiWrapper, self).__init__(*args, **kwargs)
        self.username = "admin"
        self.password = "password"
        self.url = "https://15.4.5.1"
        self.verifySsl = False
        self.api_wrapper = ForemanApiWrapper(self.username, self.password, self.url, self.verifySsl)

    # Test function naming convention:
    #
    #   test_<class function name>_<test status>_<notes>
    #

    def __cleanup_record(self, minimal_record):
        # Cleanup and delete the record if it was created
        try:
            self.api_wrapper.read_record(minimal_record)
            self.api_wrapper.delete_record(minimal_record)
        except Exception as e:
            pass

    def test_make_api_call_success(self):

        endpoint = "/api/environments"
        method = "get"

        self.api_wrapper.make_api_call(endpoint, method)

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
        endpoint = "/api/environments"
        method = "post"
        arguments = {
            "environment": {
                "name": "test_make_api_call_success_create_environment"
            }
        }
        record = arguments

        try:
            response = self.api_wrapper.make_api_call(endpoint, method, arguments)
            self.assertTrue("created_at" in response.keys())
        finally:
            self.__cleanup_record(record)

    def test_read_failure_minimal_state_does_not_exists(self):

        record_name = "test_read_failure_minimal_state_does_not_exists"
        record_type = "environment"
        minimal_record = {
            record_type: {
                "name": record_name
            }
        }

        # Null will be returned if a record does not exist
        check_record = self.api_wrapper.read_record(minimal_record)
        self.assertIsNone(check_record)


    def test_read_success_minimal_state_exists(self):

        record_name = "test_read_success_minimal_state_exists"
        record_type = "environment"
        minimal_record = {
            record_type: {
                "name": record_name
            }
        }

        try:

            # Do some cleanup
            try:
                self.api_wrapper.read_record(minimal_record)
                self.api_wrapper.delete_record(minimal_record)
            except:
                pass

            # Create the record
            self.api_wrapper.create_record(minimal_record)

            # Check that it exists
            actual_record = self.api_wrapper.read_record(minimal_record)

            self.assertIsNotNone(actual_record)
            self.assertEqual(actual_record[record_type]["name"], record_name)

            # Check that thte right record was returned
            minimalStateExists = RecordComparison.compare_records(minimal_record, actual_record)
            self.assertTrue(minimalStateExists)

        finally:
            self.__cleanup_record(minimal_record)

    def test_create_success_create_record(self):

        record_name = "test_create_success_create_record"
        record_type = "environment"
        minimal_record = {
            record_type: {
                "name": record_name
            }
        }

        try:
            actual_record_state = self.api_wrapper.create_record(minimal_record)

            self.assertIsNotNone(actual_record_state)
            self.assertEqual(type(actual_record_state), dict)

            minimalStateExists = RecordComparison.compare_records(minimal_record, actual_record_state)

            self.assertTrue(minimalStateExists)

        finally:
            self.__cleanup_record(minimal_record)

    def test_delete_success_record_deleted(self):

        record_name = "test_delete_success_record_deleted"
        record_type = "environment"
        minimal_record = {
            record_type: {
                "name": record_name
            }
        }

        try:
            # Create the record for the test
            self.api_wrapper.create_record(minimal_record)

            # Now do the test
            deleted_record = self.api_wrapper.delete_record(minimal_record)

            self.assertIsNotNone(deleted_record)
            self.assertEqual(type(deleted_record), dict)

            correctRecordDeleted = RecordComparison.compare_records(minimal_record, deleted_record)

            self.assertTrue(correctRecordDeleted)

            with self.assertRaises(Exception):
                self.api_wrapper.read_record(record_type, minimal_record)

        finally:
            self.__cleanup_record(minimal_record)