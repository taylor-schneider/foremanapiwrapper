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

    def test_check_success_minimal_state_exists(self):

        record_name = "some_environment"
        record_type = "environment"
        minimal_record_state = {
            "name": record_name
        }

        actual_record_state = self.api_state_enforcer.Check(record_type, minimal_record_state)

        self.assertIsNotNone(actual_record_state)
        self.assertEqual(actual_record_state["name"], record_name)

        minimalStateExists = self.api_state_enforcer.Compare(minimal_record_state, actual_record_state)

        self.assertTrue(minimalStateExists)

    def test_Set_CreateRecord_Success(self):

        record_name = "some_environment"
        record_type = "environment"
        minimal_record_state = {
            "name": record_name
        }

        actual_record_state = self.api_state_enforcer.Set(record_type, minimal_record_state)

        self.assertIsNotNone(actual_record_state)
        self.assertEqual(type(actual_record_state), dict)

        minimalStateExists = self.api_state_enforcer.Compare(minimal_record_state, actual_record_state)

        self.assertTrue(minimalStateExists)

    def test_Delete_DeleteRecord_Success(self):

        record_name = "some_environment"
        record_type = "environment"
        minimal_record_state = {
            "name": record_name
        }

        actualState = self.api_state_enforcer.Delete(record_type, minimal_record_state)

        self.assertIsNotNone(actualState)
        self.assertEqual(type(actualState), dict)

        correctRecordDeleted = self.api_state_enforcer.Compare(minimal_record_state, actual_record_state)

        self.assertTrue(correctRecordDeleted)