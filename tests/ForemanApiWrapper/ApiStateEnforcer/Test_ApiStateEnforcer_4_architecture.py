from tests.ForemanApiWrapper.ApiStateEnforcer.Test_ApiStateEnforcer import Test_ApiStateEnforcer
from tests.ForemanApiWrapper.ApiStateEnforcer.Test_ApiStateEnforcer_1_smartproxy import Test_ApiStateEnforcer_1_smartproxy
from tests.ForemanApiWrapper.ApiStateEnforcer.Test_ApiStateEnforcer_2_domain import Test_ApiStateEnforcer_2_domain
from tests.ForemanApiWrapper.ApiStateEnforcer.Test_ApiStateEnforcer_3_subnet import Test_ApiStateEnforcer_3_subnet

import logging

# Configure logging format and level
logFormat = '%(asctime)s,%(msecs)d %(levelname)-8s [%(module)s:%(funcName)s():%(lineno)d] %(message)s'


logging.basicConfig(format=logFormat,
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.DEBUG)


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


class Test_ApiStateEnforcer_4_architecture(Test_ApiStateEnforcer):

    def __init__(self, *args, **kwargs):
        super(Test_ApiStateEnforcer_4_architecture, self).__init__(*args, **kwargs)

    @staticmethod
    def _minimal_record():

        return {
            "architecture": {
                "name": "x86_64_test"
            }
        }

    @staticmethod
    def _create_architecture(api_state_enforcer):
        try:
            desired_state = "present"
            minimal_record = Test_ApiStateEnforcer_4_architecture._minimal_record()
            modification_receipt = api_state_enforcer.ensure_state(desired_state, minimal_record)
            return modification_receipt
        except:
            logger.warning("Utility method failed to create architecture for test case")

    @staticmethod
    def _delete_architecture(api_state_enforcer):
        try:
            desired_state = "absent"
            minimal_record = Test_ApiStateEnforcer_4_architecture._minimal_record()
            modification_receipt = api_state_enforcer.ensure_state(desired_state, minimal_record)
            return modification_receipt
        except:
            logger.warning("Utility method failed to delete architecture for test case")

    def test__architecture__create__does_not_exist(self):
        try:
            # Create prereqs
            modification_receipt = Test_ApiStateEnforcer_1_smartproxy._create_smartproxy(self.api_state_enforcer)
            smartproxy_id = modification_receipt.actual_record["smart_proxy"]["id"]
            dns_id = smartproxy_id
            dhcp_id = smartproxy_id
            tftp_id = smartproxy_id
            modification_receipt = Test_ApiStateEnforcer_2_domain._create_domain(self.api_state_enforcer, dns_id)
            domain_id = modification_receipt.actual_record["domain"]["id"]
            Test_ApiStateEnforcer_3_subnet._create_subnet(self.api_state_enforcer, domain_id, dns_id, dhcp_id, tftp_id)
            # Ensure State
            desired_state = "present"
            minimal_record = Test_ApiStateEnforcer_4_architecture._minimal_record()
            modification_receipt = self.api_state_enforcer.ensure_state(desired_state, minimal_record)
            self.assertTrue(modification_receipt.changed)
        finally:
            Test_ApiStateEnforcer_4_architecture._delete_architecture(self.api_state_enforcer)
            Test_ApiStateEnforcer_3_subnet._delete_subnet(self.api_state_enforcer, domain_id, dns_id, dhcp_id, tftp_id)
            Test_ApiStateEnforcer_2_domain._delete_domain(self.api_state_enforcer, dns_id)

    def test__architecture__create__exists(self):
        try:
            # Create prereqs
            modification_receipt = Test_ApiStateEnforcer_1_smartproxy._create_smartproxy(self.api_state_enforcer)
            smartproxy_id = modification_receipt.actual_record["smart_proxy"]["id"]
            dns_id = smartproxy_id
            dhcp_id = smartproxy_id
            tftp_id = smartproxy_id
            modification_receipt = Test_ApiStateEnforcer_2_domain._create_domain(self.api_state_enforcer, dns_id)
            domain_id = modification_receipt.actual_record["domain"]["id"]
            Test_ApiStateEnforcer_3_subnet._create_subnet(self.api_state_enforcer, domain_id, dns_id, dhcp_id, tftp_id)
            Test_ApiStateEnforcer_4_architecture._create_architecture(self.api_state_enforcer)
            # Ensure State
            desired_state = "present"
            minimal_record = Test_ApiStateEnforcer_4_architecture._minimal_record()
            modification_receipt = self.api_state_enforcer.ensure_state(desired_state, minimal_record)
            self.assertFalse(modification_receipt.changed)
        finally:
            Test_ApiStateEnforcer_4_architecture._delete_architecture(self.api_state_enforcer)
            Test_ApiStateEnforcer_3_subnet._delete_subnet(self.api_state_enforcer, domain_id, dns_id, dhcp_id, tftp_id)
            Test_ApiStateEnforcer_2_domain._delete_domain(self.api_state_enforcer, dns_id)

    def test__architecture__update(self):
        try:
            # Create prereqs
            modification_receipt = Test_ApiStateEnforcer_1_smartproxy._create_smartproxy(self.api_state_enforcer)
            smartproxy_id = modification_receipt.actual_record["smart_proxy"]["id"]
            dns_id = smartproxy_id
            dhcp_id = smartproxy_id
            tftp_id = smartproxy_id
            modification_receipt = Test_ApiStateEnforcer_2_domain._create_domain(self.api_state_enforcer, dns_id)
            domain_id = modification_receipt.actual_record["domain"]["id"]
            Test_ApiStateEnforcer_3_subnet._create_subnet(self.api_state_enforcer, domain_id, dns_id, dhcp_id, tftp_id)
            modification_receipt = Test_ApiStateEnforcer_4_architecture._create_architecture(self.api_state_enforcer)
            # Ensure State
            desired_state = "present"
            minimal_record = modification_receipt.actual_record
            minimal_record["architecture"]["name"] = "x86_64_updated"
            modification_receipt = self.api_state_enforcer.ensure_state(desired_state, minimal_record)
            self.assertTrue(modification_receipt.changed)
        finally:
            self.api_state_enforcer.ensure_state("absent", minimal_record)
            Test_ApiStateEnforcer_4_architecture._delete_architecture(self.api_state_enforcer)
            Test_ApiStateEnforcer_3_subnet._delete_subnet(self.api_state_enforcer, domain_id, dns_id, dhcp_id, tftp_id)
            Test_ApiStateEnforcer_2_domain._delete_domain(self.api_state_enforcer, dns_id)

    def test__architecture__delete(self):
        try:
            # Create prereqs
            modification_receipt = Test_ApiStateEnforcer_1_smartproxy._create_smartproxy(self.api_state_enforcer)
            smartproxy_id = modification_receipt.actual_record["smart_proxy"]["id"]
            dns_id = smartproxy_id
            dhcp_id = smartproxy_id
            tftp_id = smartproxy_id
            modification_receipt = Test_ApiStateEnforcer_2_domain._create_domain(self.api_state_enforcer, dns_id)
            domain_id = modification_receipt.actual_record["domain"]["id"]
            Test_ApiStateEnforcer_3_subnet._create_subnet(self.api_state_enforcer, domain_id, dns_id, dhcp_id, tftp_id)
            Test_ApiStateEnforcer_4_architecture._create_architecture(self.api_state_enforcer)
            # Ensure State
            desired_state = "absent"
            minimal_record = Test_ApiStateEnforcer_4_architecture._minimal_record()
            modification_receipt = self.api_state_enforcer.ensure_state(desired_state, minimal_record)
            self.assertTrue(modification_receipt.changed)
        finally:
            Test_ApiStateEnforcer_4_architecture._delete_architecture(self.api_state_enforcer)
            Test_ApiStateEnforcer_3_subnet._delete_subnet(self.api_state_enforcer, domain_id, dns_id, dhcp_id, tftp_id)
            Test_ApiStateEnforcer_2_domain._delete_domain(self.api_state_enforcer, dns_id)
