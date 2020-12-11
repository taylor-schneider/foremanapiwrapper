from tests.ForemanApiWrapper.ApiStateEnforcer.Test_ApiStateEnforcer import Test_ApiStateEnforcer
from tests.ForemanApiWrapper.ApiStateEnforcer.Test_ApiStateEnforcer_1_smartproxy import Test_ApiStateEnforcer_1_smartproxy
from tests.ForemanApiWrapper.ApiStateEnforcer.Test_ApiStateEnforcer_2_domain import Test_ApiStateEnforcer_2_domain
from tests.ForemanApiWrapper.ApiStateEnforcer.Test_ApiStateEnforcer_3_subnet import Test_ApiStateEnforcer_3_subnet
from tests.ForemanApiWrapper.ApiStateEnforcer.Test_ApiStateEnforcer_4_architecture import Test_ApiStateEnforcer_4_architecture
from tests.ForemanApiWrapper.ApiStateEnforcer.Test_ApiStateEnforcer_5_medium import Test_ApiStateEnforcer_5_medium
from tests.ForemanApiWrapper.ApiStateEnforcer.Test_ApiStateEnforcer_6_operatingsystem import Test_ApiStateEnforcer_6_operatingsystem
from tests.ForemanApiWrapper.ApiStateEnforcer.Test_ApiStateEnforcer_7_ptable import Test_ApiStateEnforcer_7_ptable
from tests.ForemanApiWrapper.ApiStateEnforcer.Test_ApiStateEnforcer_8_pxelinux_provisioning_template import Test_ApiStateEnforcer_8_pxelinux_provisioning_template
from tests.ForemanApiWrapper.ApiStateEnforcer.Test_ApiStateEnforcer_9_answefile_provisioning_template import Test_ApiStateEnforcer_9_answerfile_provisioning_template

import logging

# Configure logging format and level
logFormat = '%(asctime)s,%(msecs)d %(levelname)-8s [%(module)s:%(funcName)s():%(lineno)d] %(message)s'

logging.basicConfig(format=logFormat,
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.DEBUG)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

class Test_ApiStateEnforcer_10_link_os_with_templates(Test_ApiStateEnforcer):

    def __init__(self, *args, **kwargs):
        super(Test_ApiStateEnforcer_10_link_os_with_templates, self).__init__(*args, **kwargs)

    @staticmethod
    def _minimal_record(architecture_id, answerfile_id, medium_id, pxelinux_id, ptable_id):

        return {
            "operatingsystem": {
                "architecture_ids": [
                    architecture_id
                ],
                "config_template_ids": [
                    answerfile_id
                ],
                "description": "CentOS Operating System",
                "family": "Redhat",
                "major": "7",
                "medium_ids": [
                    medium_id
                ],
                "minor": "9.2009",
                "name": "CentOS",
                "password_hash": "SHA256",
                "provisioning_template_ids": [
                    pxelinux_id
                ],
                "ptable_ids": [
                    ptable_id
                ]
            }
        }

    @staticmethod
    def _create_operatingsystem(api_state_enforcer, architecture_id, answerfile_id, medium_id, pxelinux_id, ptable_id):
        desired_state = "present"
        minimal_record = Test_ApiStateEnforcer_10_link_os_with_templates._minimal_record(architecture_id, answerfile_id, medium_id, pxelinux_id, ptable_id)
        modification_receipt = api_state_enforcer.ensure_state(desired_state, minimal_record)
        return modification_receipt

    def test__operatingsystem__exists(self):
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
        architecture_id = modification_receipt.actual_record["architecture"]["id"]
        modification_receipt = Test_ApiStateEnforcer_5_medium._create_medium(self.api_state_enforcer)
        medium_id = modification_receipt.actual_record["medium"]["id"]
        modification_receipt = Test_ApiStateEnforcer_6_operatingsystem._create_operatingsystem(self.api_state_enforcer)
        operatingsystem_id = modification_receipt.actual_record["operatingsystem"]["id"]
        modification_receipt = Test_ApiStateEnforcer_7_ptable._create_ptable(self.api_state_enforcer)
        ptable_id = modification_receipt.actual_record["ptable"]["id"]
        modification_receipt = Test_ApiStateEnforcer_8_pxelinux_provisioning_template._create_pxelinux_provisioning_template(self.api_state_enforcer, operatingsystem_id)
        pxelinux_id = modification_receipt.actual_record["provisioning_template"]["id"]
        modification_receipt = Test_ApiStateEnforcer_9_answerfile_provisioning_template._create_answefile_provisioning_template(self.api_state_enforcer, operatingsystem_id)
        answerfile_id = modification_receipt.actual_record["provisioning_template"]["id"]
        Test_ApiStateEnforcer_10_link_os_with_templates._create_operatingsystem(self.api_state_enforcer, architecture_id, answerfile_id, medium_id, pxelinux_id, ptable_id)
        # Ensure State
        desired_state = "present"
        minimal_record = Test_ApiStateEnforcer_10_link_os_with_templates._minimal_record(architecture_id, answerfile_id, medium_id, pxelinux_id, ptable_id)
        modification_receipt = self.api_state_enforcer.ensure_state(desired_state, minimal_record)
        self.assertFalse(modification_receipt.changed)

    def test__answerfile_provisioning_template__update(self):
        self.fail("Not implemented")
