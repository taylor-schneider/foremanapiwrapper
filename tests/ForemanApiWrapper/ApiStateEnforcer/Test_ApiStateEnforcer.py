from unittest import TestCase
from ForemanApiWrapper.ForemanApiUtilities.ForemanApiWrapper import ForemanApiWrapper
from ForemanApiWrapper.ApiStateEnforcer.ApiStateEnforcer import ApiStateEnforcer
from ForemanApiWrapper.ApiStateEnforcer.RecordModificationReceipt import RecordModificationReceipt

class Test_ApiStateEnforcer(TestCase):

    def __init__(self, *args, **kwargs):
        super(Test_ApiStateEnforcer, self).__init__(*args, **kwargs)
        self.username = "admin"
        self.password = "password"
        self.url = "https://15.4.7.1"
        self.verifySsl = False
        self.api_wrapper = ForemanApiWrapper(self.username, self.password, self.url, self.verifySsl)
        self.api_state_enforcer = ApiStateEnforcer(self.api_wrapper)


    def test_ensure_state_exists_create_record(self):

        record_name = "some_environment"
        record_type = "environment"
        minimal_record_state = {
            "name": record_name
        }
        desired_state = "present"

        try:

            with self.assertRaises(Exception) as e:
                 self.api_state_enforcer.ReadRecord(record_type, minimal_record_state)

            modification_receipt = self.api_state_enforcer.ensure_state(record_type, desired_state, minimal_record_state)

            self.assertIsNotNone(modification_receipt)
            self.assertEqual(type(modification_receipt), RecordModificationReceipt)
            self.assertTrue(modification_receipt.changed)

        finally:
            self.api_state_enforcer.ensure_state(record_type, "absent", minimal_record_state)

        def test_ensure_state_noes_not_exist(self):
            record_name = "some_environment"
            record_type = "environment"
            minimal_record_state = {
                "name": record_name
            }
            desired_state = "absent"

            actual_record_state = self.api_state_enforcer.ensure_state(record_type, desired_state, minimal_record_state)

            self.assertIsNotNone(actual_record_state)
            self.assertEqual(type(actual_record_state), dict)

            minimalStateExists = self.api_state_enforcer.ensure_state(record_type, desired_state, minimal_record_state)

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
                actual_record_state = self.api_state_enforcer.ReadRecord(record_type, minimal_record_state)

            modification_receipt = self.api_state_enforcer.ensure_state(record_type, desired_state, minimal_record_state)

            modification_receipt = self.api_state_enforcer.ensure_state(record_type, desired_state, minimal_record_state)

            self.assertIsNotNone(modification_receipt)
            self.assertEqual(type(modification_receipt), RecordModificationReceipt)
            self.assertFalse(modification_receipt.changed)

        finally:
            self.api_state_enforcer.ensure_state(record_type, "absent", minimal_record_state)