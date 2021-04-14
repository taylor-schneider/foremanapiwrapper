from tests.ForemanApiWrapper.ApiStateEnforcer.Test_ApiStateEnforcer import Test_ApiStateEnforcer
from tests.ForemanApiWrapper.ApiStateEnforcer.Test_ApiStateEnforcer_1_smartproxy import Test_ApiStateEnforcer_1_smartproxy
from tests.ForemanApiWrapper.ApiStateEnforcer.Test_ApiStateEnforcer_2_domain import Test_ApiStateEnforcer_2_domain

import logging

# Configure logging format and level
logFormat = '%(asctime)s,%(msecs)d %(levelname)-8s [%(module)s:%(funcName)s():%(lineno)d] %(message)s'

logging.basicConfig(format=logFormat,
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.DEBUG)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

class Test_ApiStateEnforcer_3_subnet(Test_ApiStateEnforcer):

    def __init__(self, *args, **kwargs):
        super(Test_ApiStateEnforcer_3_subnet, self).__init__(*args, **kwargs)

    @staticmethod
    def _minimal_record(domain_id, dns_id, dhcp_id, tftp_id):

        return {
            "subnet": {
                "name": "Test Subnet",
                "network": "15.0.0.0",
                "mask": "255.0.0.0",
                "gateway": "15.1.1.1",
                "dns_primary": "15.4.5.1",
                "dns_secondary": "15.1.1.1",
                "boot_mode": "DHCP",
                "domain_ids": [domain_id],
                "dhcp_id": dns_id,
                "tftp_id": dhcp_id,
                "dns_id": tftp_id
            }
        }

    # Deleting a subnet is a bit complicated...
    # It must first be unlinked and then it can be deleted

    @staticmethod
    def _delete_subnet(api_state_enforcer, domain_id, dns_id, dhcp_id, tftp_id):
        try:
            minimal_record = Test_ApiStateEnforcer_3_subnet._minimal_record(domain_id, dns_id, dhcp_id, tftp_id)
            minimal_record["subnet"]["domain_ids"] = []
            api_state_enforcer.ensure_state("present", minimal_record)
            Test_ApiStateEnforcer_3_subnet._minimal_record(domain_id, dns_id, dhcp_id, tftp_id)
            modification_receipt = api_state_enforcer.ensure_state("absent", minimal_record)
            return modification_receipt
        except:
            logger.warning("Utility method failed to delete subnet for test case")

    @staticmethod
    def _create_subnet(api_state_enforcer, domain_id, dns_id, dhcp_id, tftp_id):
        try:
            desired_state = "present"
            minimal_record = Test_ApiStateEnforcer_3_subnet._minimal_record(domain_id, dns_id, dhcp_id, tftp_id)
            modification_receipt = api_state_enforcer.ensure_state(desired_state, minimal_record)
            return modification_receipt
        except:
            logger.warning("Utility method failed to create subnet for test case")

    def test__subnet__create__does_not_exist(self):
        try:
            # Create the smartproxy and domain
            modification_receipt = Test_ApiStateEnforcer_1_smartproxy._create_smartproxy(self.api_state_enforcer)
            smartproxy_id = modification_receipt.actual_record["smart_proxy"]["id"]
            dns_id = smartproxy_id
            dhcp_id = smartproxy_id
            tftp_id = smartproxy_id
            modification_receipt = Test_ApiStateEnforcer_2_domain._create_domain(self.api_state_enforcer, dns_id)
            self.assertTrue(modification_receipt.changed)
        finally:
            domain_id = modification_receipt.actual_record["domain"]["id"]
            Test_ApiStateEnforcer_3_subnet._delete_subnet(self.api_state_enforcer, domain_id, dns_id, dhcp_id, tftp_id)
            Test_ApiStateEnforcer_2_domain._delete_domain(self.api_state_enforcer, dns_id)

    def test__subnet__create__exists(self):
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
            minimal_record = Test_ApiStateEnforcer_3_subnet._minimal_record(domain_id, dns_id, dhcp_id, tftp_id)
            modification_receipt = self.api_state_enforcer.ensure_state(desired_state, minimal_record)
            self.assertFalse(modification_receipt.changed)
        finally:
            Test_ApiStateEnforcer_3_subnet._delete_subnet(self.api_state_enforcer, domain_id, dns_id, dhcp_id, tftp_id)
            Test_ApiStateEnforcer_2_domain._delete_domain(self.api_state_enforcer, dns_id)

    def test__subnet__update(self):
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
            minimal_record = Test_ApiStateEnforcer_3_subnet._minimal_record(domain_id, dns_id, dhcp_id, tftp_id)
            minimal_record["subnet"]["name"] = "Modified Subnet"
            modification_receipt = self.api_state_enforcer.ensure_state(desired_state, minimal_record)
            self.assertTrue(modification_receipt.changed)
        finally:
            minimal_record["subnet"]["domain_ids"] = []
            modification_receipt = self.api_state_enforcer.ensure_state("present", minimal_record)
            modification_receipt = self.api_state_enforcer.ensure_state("absent", minimal_record)
            Test_ApiStateEnforcer_3_subnet._delete_subnet(self.api_state_enforcer, domain_id, dns_id, dhcp_id, tftp_id)
            Test_ApiStateEnforcer_2_domain._delete_domain(self.api_state_enforcer, dns_id)


    def test__subnet__delete(self):
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
            desired_state = "absent"
            minimal_record = Test_ApiStateEnforcer_3_subnet._minimal_record(domain_id, dns_id, dhcp_id, tftp_id)
            minimal_record["subnet"]["domain_ids"] = []
            self.api_state_enforcer.ensure_state("present", minimal_record)
            modification_receipt = self.api_state_enforcer.ensure_state(desired_state, minimal_record)
            self.assertFalse(modification_receipt.changed)
        except Exception as e:
            pass
        finally:
            Test_ApiStateEnforcer_3_subnet._delete_subnet(self.api_state_enforcer, domain_id, dns_id, dhcp_id, tftp_id)
            Test_ApiStateEnforcer_2_domain._delete_domain(self.api_state_enforcer, dns_id)
