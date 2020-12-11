from tests.ForemanApiWrapper.ApiStateEnforcer.Test_ApiStateEnforcer import Test_ApiStateEnforcer
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

class Test_ApiStateEnforcer_1_smartproxy(Test_ApiStateEnforcer):

    def __init__(self, *args, **kwargs):
        super(Test_ApiStateEnforcer_1_smartproxy, self).__init__(*args, **kwargs)

    @staticmethod
    def _minimal_record():

        return {
            "smart_proxy": {
                "name": "foreman.foobar.com",
                "features": [
                    {"name": "TFTP"},
                    {"name": "DNS"},
                    {"name": "DHCP"}
                ]
            }
        }

    @staticmethod
    def _create_smartproxy(api_state_enforcer):
        desired_state = "present"
        minimal_record = Test_ApiStateEnforcer_1_smartproxy._minimal_record()
        modification_receipt = api_state_enforcer.ensure_state(desired_state, minimal_record)
        return modification_receipt

    def test__smartproxy__create(self):
        self.fail("Not implemented")

    def test__smartproxy_exists(self):
        Test_ApiStateEnforcer_1_smartproxy._create_smartproxy(self.api_state_enforcer)
        desired_state = "present"
        minimal_record = Test_ApiStateEnforcer_1_smartproxy._minimal_record()
        modification_receipt = self.api_state_enforcer.ensure_state(desired_state, minimal_record)
        self.assertFalse(modification_receipt.changed)

    def test__smartproxy__update(self):
        self.fail("Not implemented")

    def test__smartproxy__delete(self):
        self.fail("Not implemented")