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
                "name": "foreman.foobar.com",
                "dns_id": dns_id
            }
        }

    @staticmethod
    def _create_domain(api_state_enforcer, dns_id):
        desired_state = "present"
        minimal_record = Test_ApiStateEnforcer_2_domain._minimal_record(dns_id)
        modification_receipt = api_state_enforcer.ensure_state(desired_state, minimal_record)
        return modification_receipt

    def test__domain__create(self):
        self.fail("Not implemented")

    def test__domain_exists(self):
        # Create Prereqs
        modification_result = Test_ApiStateEnforcer_1_smartproxy._create_smartproxy(self.api_state_enforcer)
        dns_id = modification_result.actual_record["smart_proxy"]["id"]
        # Ensure State
        desired_state = "present"
        minimal_record = Test_ApiStateEnforcer_2_domain._minimal_record(dns_id)
        modification_receipt = self.api_state_enforcer.ensure_state(desired_state, minimal_record)
        self.assertFalse(modification_receipt.changed)

    def test__domain__update(self):
        self.fail("Not implemented")

    def test__domain__delete(self):
        self.fail("Not implemented")
