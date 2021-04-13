from tests.ForemanApiWrapper.ApiStateEnforcer.Test_ApiStateEnforcer import Test_ApiStateEnforcer
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
                ],
                "url": "https://foreman.foobar.com:8443"
            }
        }

    @staticmethod
    def _delete_smartproxy(api_state_enforcer):
        desired_state = "absent"
        minimal_record = Test_ApiStateEnforcer_1_smartproxy._minimal_record()
        modification_receipt = api_state_enforcer.ensure_state(desired_state, minimal_record)
        return modification_receipt

    @staticmethod
    def _create_smartproxy(api_state_enforcer):
        desired_state = "present"
        minimal_record = Test_ApiStateEnforcer_1_smartproxy._minimal_record()
        modification_receipt = api_state_enforcer.ensure_state(desired_state, minimal_record)
        return modification_receipt

    def test__smartproxy__create_does_not_exist(self):
        # The smartproxy is created by default when installing foreman
        # It is too difficult at this point in time to figure out how to
        # orchestrate a siguation where one can be created, updated, or deleted.
        self.fail("Not implemented")

    def test__smartproxy_create_exists(self):
        Test_ApiStateEnforcer_1_smartproxy._create_smartproxy(self.api_state_enforcer)
        desired_state = "present"
        minimal_record = Test_ApiStateEnforcer_1_smartproxy._minimal_record()
        modification_receipt = self.api_state_enforcer.ensure_state(desired_state, minimal_record)
        self.assertFalse(modification_receipt.changed)

    def test__smartproxy__update(self):
        # The smartproxy is created by default when installing foreman
        # It is too difficult at this point in time to figure out how to
        # orchestrate a siguation where one can be created, updated, or deleted.
        self.fail("Not implemented")

    def test__smartproxy__delete(self):
        # The smartproxy is created by default when installing foreman
        # It is too difficult at this point in time to figure out how to
        # orchestrate a siguation where one can be created, updated, or deleted.
        self.fail("Not implemented")
