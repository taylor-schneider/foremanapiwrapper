from tests.ForemanApiWrapper.ApiStateEnforcer.Test_ApiStateEnforcer import Test_ApiStateEnforcer
from tests.ForemanApiWrapper.ApiStateEnforcer.Test_ApiStateEnforcer_1_smartproxy import Test_ApiStateEnforcer_1_smartproxy
from tests.ForemanApiWrapper.ApiStateEnforcer.Test_ApiStateEnforcer_2_domain import Test_ApiStateEnforcer_2_domain
from tests.ForemanApiWrapper.ApiStateEnforcer.Test_ApiStateEnforcer_3_subnet import Test_ApiStateEnforcer_3_subnet
from tests.ForemanApiWrapper.ApiStateEnforcer.Test_ApiStateEnforcer_4_architecture import Test_ApiStateEnforcer_4_architecture
from tests.ForemanApiWrapper.ApiStateEnforcer.Test_ApiStateEnforcer_5_medium import Test_ApiStateEnforcer_5_medium
from tests.ForemanApiWrapper.ApiStateEnforcer.Test_ApiStateEnforcer_6_operatingsystem import Test_ApiStateEnforcer_6_operatingsystem


import logging

# Configure logging format and level
logFormat = '%(asctime)s,%(msecs)d %(levelname)-8s [%(module)s:%(funcName)s():%(lineno)d] %(message)s'

logging.basicConfig(format=logFormat,
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.DEBUG)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

class Test_ApiStateEnforcer_7_ptable(Test_ApiStateEnforcer):

    def __init__(self, *args, **kwargs):
        super(Test_ApiStateEnforcer_7_ptable, self).__init__(*args, **kwargs)

    @staticmethod
    def __minimal_record():

        return {
            "ptable": {
                "layout": """<%#

    kind: ptable

    name: CentOS Partition Table

    model: Ptable

    oses:

    - CentOS

    -%>""",
                "name": "CentOS 7.9.2009 Partition Table",
                "operatingsystem_ids": [
                    '1'
                ],
                "os_family": "Redhat"
            }
        }

    @staticmethod
    def _create_ptable(api_state_enforcer):
        desired_state = "present"
        minimal_record = Test_ApiStateEnforcer_7_ptable.__minimal_record()
        modification_receipt = api_state_enforcer.ensure_state(desired_state, minimal_record)
        return modification_receipt

    def test__ptable__create(self):
        self.fail("Not implemented")

    def test__ptable_exists(self):
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
        Test_ApiStateEnforcer_7_ptable._create_ptable(self.api_state_enforcer)
        # Ensure State
        desired_state = "present"
        minimal_record = Test_ApiStateEnforcer_7_ptable.__minimal_record()
        modification_receipt = self.api_state_enforcer.ensure_state(desired_state, minimal_record)
        self.assertFalse(modification_receipt.changed)

    def test__ptable__update(self):
        self.fail("Not implemented")

    def test__ptable__delete(self):
        self.fail("Not implemented")