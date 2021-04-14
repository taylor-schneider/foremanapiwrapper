from tests.ForemanApiWrapper.ApiStateEnforcer.Test_ApiStateEnforcer import Test_ApiStateEnforcer
from tests.ForemanApiWrapper.ApiStateEnforcer.Test_ApiStateEnforcer_1_smartproxy import Test_ApiStateEnforcer_1_smartproxy
from ForemanApiWrapper.ForemanApiUtilities.ForemanApiWrapper import ForemanApiWrapper
from ForemanApiWrapper.ApiStateEnforcer.ApiStateEnforcer import ApiStateEnforcer

import logging

# Configure logging format and level
logFormat = '%(asctime)s,%(msecs)d %(levelname)-8s [%(module)s:%(funcName)s():%(lineno)d] %(message)s'

logging.basicConfig(format=logFormat,
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.DEBUG)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

class Test_ApiStateEnforcer_2_domain(Test_ApiStateEnforcer):

    def __init__(self, *args, **kwargs):
        super(Test_ApiStateEnforcer_2_domain, self).__init__(*args, **kwargs)

    @staticmethod
    def _minimal_record(dns_id):

        return {
            "domain": {
                "name": "test.foobar.com",
                "dns_id": dns_id
            }
        }

    @staticmethod
    def _delete_domain(api_state_enforcer, dns_id):
        try:
            desired_state = "absent"
            minimal_record = Test_ApiStateEnforcer_2_domain._minimal_record(dns_id)
            modification_receipt = api_state_enforcer.ensure_state(desired_state, minimal_record)
            return modification_receipt
        except:
            logger.warning("Utility method failed to delete domain for test case")
            pass

    @staticmethod
    def _create_domain(api_state_enforcer, dns_id):
        try:
            desired_state = "present"
            minimal_record = Test_ApiStateEnforcer_2_domain._minimal_record(dns_id)
            modification_receipt = api_state_enforcer.ensure_state(desired_state, minimal_record)
            return modification_receipt
        except:
            logger.warning("Utility method failed to create domain for test case")
            pass

    def test__domain__create(self):
        try:
            # Create prereqs
            modification_result = Test_ApiStateEnforcer_1_smartproxy._create_smartproxy(self.api_state_enforcer)
            dns_id = modification_result.actual_record["smart_proxy"]["id"]
            # Ensure the state
            modification_receipt = Test_ApiStateEnforcer_2_domain._create_domain(self.api_state_enforcer, dns_id)
            self.assertTrue(modification_receipt.changed)
        finally:
            # Cleanup from past runs
            Test_ApiStateEnforcer_2_domain._delete_domain(self.api_state_enforcer, dns_id)

    def test__domain_exists(self):
        try:
            # Create Prereqs
            modification_receipt = Test_ApiStateEnforcer_1_smartproxy._create_smartproxy(self.api_state_enforcer)
            dns_id = modification_receipt.actual_record["smart_proxy"]["id"]
            Test_ApiStateEnforcer_2_domain._create_domain(self.api_state_enforcer, dns_id)
            # Ensure State
            desired_state = "present"
            minimal_record = Test_ApiStateEnforcer_2_domain._minimal_record(dns_id)
            modification_receipt = self.api_state_enforcer.ensure_state(desired_state, minimal_record)
            self.assertFalse(modification_receipt.changed)
        finally:
            # Cleanup from past runs
            Test_ApiStateEnforcer_2_domain._delete_domain(self.api_state_enforcer, dns_id)

    def test__domain__update(self):
        try:
            # Create Prereqs
            modification_receipt = Test_ApiStateEnforcer_1_smartproxy._create_smartproxy(self.api_state_enforcer)
            dns_id = modification_receipt.actual_record["smart_proxy"]["id"]
            modification_receipt = Test_ApiStateEnforcer_2_domain._create_domain(self.api_state_enforcer, dns_id)

            # Ensure State
            desired_state = "present"
            update_record = modification_receipt.actual_record.copy()
            update_record["domain"]["name"] = "modify.foobar.com"
            modification_receipt = self.api_state_enforcer.ensure_state(desired_state, update_record)
            self.assertTrue(modification_receipt.changed)
        finally:
            self.api_state_enforcer.ensure_state("absent", update_record)
            Test_ApiStateEnforcer_2_domain._delete_domain(self.api_state_enforcer, dns_id)

    def test__domain__delete(self):
        try:
            # Create Prereqs
            modification_receipt = Test_ApiStateEnforcer_1_smartproxy._create_smartproxy(self.api_state_enforcer)
            dns_id = modification_receipt.actual_record["smart_proxy"]["id"]
            Test_ApiStateEnforcer_2_domain._create_domain(self.api_state_enforcer, dns_id)
            # Ensure State
            desired_state = "absent"
            minimal_record = Test_ApiStateEnforcer_2_domain._minimal_record(dns_id)
            modification_receipt = self.api_state_enforcer.ensure_state(desired_state, minimal_record)
            self.assertTrue(modification_receipt.changed)
        finally:
            # Cleanup from past runs
            Test_ApiStateEnforcer_2_domain._delete_domain(self.api_state_enforcer, dns_id)
