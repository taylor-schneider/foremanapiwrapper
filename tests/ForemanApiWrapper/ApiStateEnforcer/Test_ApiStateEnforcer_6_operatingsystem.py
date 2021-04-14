from tests.ForemanApiWrapper.ApiStateEnforcer.Test_ApiStateEnforcer import Test_ApiStateEnforcer
from tests.ForemanApiWrapper.ApiStateEnforcer.Test_ApiStateEnforcer_1_smartproxy import Test_ApiStateEnforcer_1_smartproxy
from tests.ForemanApiWrapper.ApiStateEnforcer.Test_ApiStateEnforcer_2_domain import Test_ApiStateEnforcer_2_domain
from tests.ForemanApiWrapper.ApiStateEnforcer.Test_ApiStateEnforcer_3_subnet import Test_ApiStateEnforcer_3_subnet
from tests.ForemanApiWrapper.ApiStateEnforcer.Test_ApiStateEnforcer_4_architecture import Test_ApiStateEnforcer_4_architecture
from tests.ForemanApiWrapper.ApiStateEnforcer.Test_ApiStateEnforcer_5_medium import Test_ApiStateEnforcer_5_medium


import logging

# Configure logging format and level
logFormat = '%(asctime)s,%(msecs)d %(levelname)-8s [%(module)s:%(funcName)s():%(lineno)d] %(message)s'

logging.basicConfig(format=logFormat,
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.DEBUG)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

class Test_ApiStateEnforcer_6_operatingsystem(Test_ApiStateEnforcer):

    def __init__(self, *args, **kwargs):
        super(Test_ApiStateEnforcer_6_operatingsystem, self).__init__(*args, **kwargs)

    @staticmethod
    def _minimal_record():

        return {
            "operatingsystem": {
                "architecture_ids": [],
                "config_template_ids": [],
                "description": "CentOS Test Operating System",
                "family": "Redhat",
                "major": "6",
                "medium_ids": [],
                "minor": "6.6666",
                "name": "TestCentos",
                "password_hash": "SHA256",
                "provisioning_template_ids": [],
                "ptable_ids": []
            }
        }

    # Note: When you intall foreman it will autoscan a host and automagically assume a name for an os
    # The name would be CentOS
    # We dont want to use this name because we do not want to mess with that os

    @staticmethod
    def _delete_operatingsystem(api_state_enforcer):
        try:
            desired_state = "absent"
            minimal_record = Test_ApiStateEnforcer_6_operatingsystem._minimal_record()
            modification_receipt = api_state_enforcer.ensure_state(desired_state, minimal_record)
            return modification_receipt
        except:
            logger.warning("Utility method failed to delete operatingsystem for test case")

    @staticmethod
    def _create_operatingsystem(api_state_enforcer):
        try:
            desired_state = "present"
            minimal_record = Test_ApiStateEnforcer_6_operatingsystem._minimal_record()
            modification_receipt = api_state_enforcer.ensure_state(desired_state, minimal_record)
            return modification_receipt
        except:
            logger.warning("Utility method failed to delete operatingsystem for test case")

    def test__operatingsystem__create__does_not_exist(self):
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
            Test_ApiStateEnforcer_5_medium._create_medium(self.api_state_enforcer)
            # Ensure State
            desired_state = "present"
            minimal_record = Test_ApiStateEnforcer_6_operatingsystem._minimal_record()
            modification_receipt = self.api_state_enforcer.ensure_state(desired_state, minimal_record)
            self.assertTrue(modification_receipt.changed)
        finally:
            Test_ApiStateEnforcer_6_operatingsystem._delete_operatingsystem(self.api_state_enforcer)
            Test_ApiStateEnforcer_5_medium._delete_medium(self.api_state_enforcer)
            Test_ApiStateEnforcer_4_architecture._delete_architecture(self.api_state_enforcer)
            Test_ApiStateEnforcer_3_subnet._delete_subnet(self.api_state_enforcer, domain_id, dns_id, dhcp_id, tftp_id)
            Test_ApiStateEnforcer_2_domain._delete_domain(self.api_state_enforcer, dns_id)

    def test__operatingsystem__create__already_exists(self):
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
            Test_ApiStateEnforcer_5_medium._create_medium(self.api_state_enforcer)
            Test_ApiStateEnforcer_6_operatingsystem._create_operatingsystem(self.api_state_enforcer)
            # Ensure State
            desired_state = "present"
            minimal_record = Test_ApiStateEnforcer_6_operatingsystem._minimal_record()
            modification_receipt = self.api_state_enforcer.ensure_state(desired_state, minimal_record)
            self.assertFalse(modification_receipt.changed)
        finally:
            Test_ApiStateEnforcer_6_operatingsystem._delete_operatingsystem(self.api_state_enforcer)
            Test_ApiStateEnforcer_5_medium._delete_medium(self.api_state_enforcer)
            Test_ApiStateEnforcer_4_architecture._delete_architecture(self.api_state_enforcer)
            Test_ApiStateEnforcer_3_subnet._delete_subnet(self.api_state_enforcer, domain_id, dns_id, dhcp_id, tftp_id)
            Test_ApiStateEnforcer_2_domain._delete_domain(self.api_state_enforcer, dns_id)

    def test__operatingsystem__update(self):
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
            Test_ApiStateEnforcer_5_medium._create_medium(self.api_state_enforcer)
            modification_receipt = Test_ApiStateEnforcer_6_operatingsystem._create_operatingsystem(self.api_state_enforcer)

            # Ensure State
            desired_state = "present"
            dup_record = modification_receipt.actual_record.copy()
            dup_record["operatingsystem"]["minor"] = "6666.6"
            modification_receipt = self.api_state_enforcer.ensure_state(desired_state, dup_record)
            self.assertTrue(modification_receipt.changed)
        finally:
            self.api_state_enforcer.ensure_state("absent", dup_record)
            Test_ApiStateEnforcer_6_operatingsystem._delete_operatingsystem(self.api_state_enforcer)
            Test_ApiStateEnforcer_5_medium._delete_medium(self.api_state_enforcer)
            Test_ApiStateEnforcer_4_architecture._delete_architecture(self.api_state_enforcer)
            Test_ApiStateEnforcer_3_subnet._delete_subnet(self.api_state_enforcer, domain_id, dns_id, dhcp_id, tftp_id)
            Test_ApiStateEnforcer_2_domain._delete_domain(self.api_state_enforcer, dns_id)

    def test__operatingsystem__delete(self):
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
            Test_ApiStateEnforcer_5_medium._create_medium(self.api_state_enforcer)
            modification_receipt = Test_ApiStateEnforcer_6_operatingsystem._create_operatingsystem(self.api_state_enforcer)

            # Ensure State
            desired_state = "absent"
            dup_record = modification_receipt.actual_record.copy()
            dup_record["operatingsystem"]["minor"] = "6666.6"
            modification_receipt = self.api_state_enforcer.ensure_state(desired_state, dup_record)
            self.assertTrue(modification_receipt.changed)
        finally:
            Test_ApiStateEnforcer_6_operatingsystem._delete_operatingsystem(self.api_state_enforcer)
            Test_ApiStateEnforcer_5_medium._delete_medium(self.api_state_enforcer)
            Test_ApiStateEnforcer_4_architecture._delete_architecture(self.api_state_enforcer)
            Test_ApiStateEnforcer_3_subnet._delete_subnet(self.api_state_enforcer, domain_id, dns_id, dhcp_id, tftp_id)
            Test_ApiStateEnforcer_2_domain._delete_domain(self.api_state_enforcer, dns_id)
