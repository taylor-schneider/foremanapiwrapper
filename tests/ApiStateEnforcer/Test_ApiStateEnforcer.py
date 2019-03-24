from unittest import TestCase
from ForemanApiUtilities.ForemanApiWrapper import ForemanApiWrapper
from ApiStateEnforcer.ApiStateEnforcer import ApiStateEnforcer


class Test_ApiStateEnforcer(TestCase):

    def __init__(self, *args, **kwargs):
        super(Test_ApiStateEnforcer, self).__init__(*args, **kwargs)
        self.username = "admin"
        self.password = "password"
        self.url = "https://15.4.7.1"
        self.verifySsl = False
        self.api_wrapper = ForemanApiWrapper(self.username, self.password, self.url, self.verifySsl)
        self.api_state_enforcer = ApiStateEnforcer(self.api_wrapper)

    # Test function naming convention:
    #
    #   test_<class function name>_<test status>_<notes>
    #

    def test_check_success_minimal_state_does_not_exists(self):

        record_name = "this_should_not_exist"
        record_type = "environment"
        minimal_record_state = {
            "name": record_name
        }

        # An Exception should be raised if the record does not exist
        with self.assertRaises(Exception) as e:
            actual_record_state = self.api_state_enforcer.Check(record_type, minimal_record_state)

    def test_check_success_minimal_state_exists(self):

        record_name = "some_environment"
        record_type = "environment"
        minimal_record_state = {
            "name": record_name
        }

        try:

            # An Exception should be raised if the record does not exist
            with self.assertRaises(Exception):
                actual_record_state = self.api_state_enforcer.Check(record_type, minimal_record_state)

            # Create the record
            self.api_state_enforcer.EnsureState(record_type, "present", minimal_record_state)

            # Check that it exists
            actual_record_state = self.api_state_enforcer.Check(record_type, minimal_record_state)

            self.assertIsNotNone(actual_record_state)
            self.assertEqual(actual_record_state["name"], record_name)

            # Check that thte right record was returned
            minimalStateExists = self.api_state_enforcer.Compare(minimal_record_state, actual_record_state)

            self.assertTrue(minimalStateExists)
        finally:
            self.api_state_enforcer.EnsureState(record_type, "absent", minimal_record_state)

    def test_set_success_create_record(self):

        record_name = "some_environment"
        record_type = "environment"
        minimal_record_state = {
            "name": record_name
        }

        try:
            actual_record_state = self.api_state_enforcer.Set(record_type, minimal_record_state)

            self.assertIsNotNone(actual_record_state)
            self.assertEqual(type(actual_record_state), dict)

            minimalStateExists = self.api_state_enforcer.Compare(minimal_record_state, actual_record_state)

            self.assertTrue(minimalStateExists)
        finally:
            self.api_state_enforcer.EnsureState(record_type, "absent", minimal_record_state)

    def test_delete_success_record_deleted(self):

        record_name = "some_environment"
        record_type = "environment"
        minimal_record_state = {
            "name": record_name
        }

        # Create the record for the test
        self.api_state_enforcer.EnsureState(record_type, "present", minimal_record_state)

        # Now do the test
        actual_record_state = self.api_state_enforcer.Delete(record_type, minimal_record_state)

        self.assertIsNotNone(actual_record_state)
        self.assertEqual(type(actual_record_state), dict)

        correctRecordDeleted = self.api_state_enforcer.Compare(minimal_record_state, actual_record_state)

        self.assertTrue(correctRecordDeleted)

    def test_ensure_state_exists_create_record(self):

        record_name = "some_environment"
        record_type = "environment"
        minimal_record_state = {
            "name": record_name
        }
        desired_state = "present"

        try:

            with self.assertRaises(Exception) as e:
                actual_record_state = self.api_state_enforcer.Check(record_type, minimal_record_state)

            state_report = self.api_state_enforcer.EnsureState(record_type, desired_state, minimal_record_state)

            self.assertIsNotNone(state_report)
            self.assertEqual(type(state_report), dict)
            self.assertTrue(state_report["changed"])

        finally:
            self.api_state_enforcer.EnsureState(record_type, "absent", minimal_record_state)

        def test_ensure_state_noes_not_exist(self):
            record_name = "some_environment"
            record_type = "environment"
            minimal_record_state = {
                "name": record_name
            }
            desired_state = "absent"

            actual_record_state = self.api_state_enforcer.EnsureState(record_type, desired_state, minimal_record_state)

            self.assertIsNotNone(actual_record_state)
            self.assertEqual(type(actual_record_state), dict)

            minimalStateExists = self.api_state_enforcer.EnsureState(record_type, desired_state, minimal_record_state)

            self.assertTrue(minimalStateExists)

    def test_ensure_state_exists_record_exists(self):

        record_name = "some_environment"
        record_type = "environment"
        minimal_record_state = {
            "name": record_name
        }
        desired_state = "present"

        try:

            with self.assertRaises(Exception) as e:
                actual_record_state = self.api_state_enforcer.Check(record_type, minimal_record_state)

            state_report = self.api_state_enforcer.EnsureState(record_type, desired_state, minimal_record_state)

            state_report = self.api_state_enforcer.EnsureState(record_type, desired_state, minimal_record_state)

            self.assertIsNotNone(state_report)
            self.assertEqual(type(state_report), dict)
            self.assertFalse(state_report["changed"])

        finally:
            self.api_state_enforcer.EnsureState(record_type, "absent", minimal_record_state)