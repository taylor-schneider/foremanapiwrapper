from unittest import TestCase
from ForemanApiWrapper.ForemanApiUtilities.ForemanApiWrapper import ForemanApiWrapper
from ForemanApiWrapper.RecordUtilities import RecordComparison


class Test_ForemanApiWrapper(TestCase):

    def __init__(self, *args, **kwargs):
        super(Test_ForemanApiWrapper, self).__init__(*args, **kwargs)
        self.username = "admin"
        self.password = "password"
        self.url = "https://15.4.7.1"
        self.verifySsl = False
        self.api_wrapper = ForemanApiWrapper(self.username, self.password, self.url, self.verifySsl)

    # Test function naming convention:
    #
    #   test_<class function name>_<test status>_<notes>
    #

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
        arguments =  {
            "environment": {
                "name": "some_environment"
            }
        }

        response = self.api_wrapper.make_api_call(endpoint, method, arguments)
        self.assertTrue("created_at" in response.keys())

    def test_read_failure_minimal_state_does_not_exists(self):

        record_name = "this_should_not_exist"
        record_type = "environment"
        minimal_record = {
            record_type: {
                "name": record_name
            }
        }

        # An Exception should be raised if the record does not exist
        with self.assertRaises(Exception) as exceptionContext:
            self.api_wrapper.read_record(minimal_record)

        # Verify the correct exception is thrown
        # If not, rethrow the original exception so we can debug the issue
        try:
            s = 'An error occurred while reading the record.'
            e = exceptionContext.exception
            self.assertEqual(e.args[0], s)
            s = "Resource environment not found by id '{0}'".format(record_name)
            e = exceptionContext.exception.__cause__
            self.assertEqual(e.args[0], s)
        except:
            raise exceptionContext.exception

    def test_read_success_minimal_state_exists(self):

        record_name = "some_environment"
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
            minimalStateExists = RecordComparison.compare_records(minimal_record, actual_record, self.api_wrapper.property_name_mappings)
            self.assertTrue(minimalStateExists)

        finally:
            # Cleanup and delete the record if it was created
            try:
                self.api_wrapper.read_record(minimal_record)
                self.api_wrapper.delete_record(minimal_record)
            except Exception as e:
                pass

    def test_create_success_create_record(self):

        record_name = "some_environment"
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

            minimalStateExists = RecordComparison.compare_records(minimal_record, actual_record_state, self.api_wrapper.property_name_mappings)

            self.assertTrue(minimalStateExists)

        finally:
            # Cleanup and delete the record if it was created
            try:
                self.api_wrapper.read_record(minimal_record)
                self.api_wrapper.delete_record(minimal_record)
            except Exception as e:
                pass

    def test_delete_success_record_deleted(self):

        record_name = "some_environment"
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

            correctRecordDeleted = RecordComparison.compare_records(minimal_record, deleted_record, self.api_wrapper.property_name_mappings)

            self.assertTrue(correctRecordDeleted)

            with self.assertRaises(Exception):
                self.api_wrapper.read_record(record_type, minimal_record)

        finally:
            # Cleanup and delete the record if it was created
            try:
                self.api_wrapper.read_record(record_type, minimal_record)
                self.api_wrapper.delete_record(record_type, minimal_record)
            except Exception as e:
                pass