from unittest import TestCase
from ForemanApiWrapper.ForemanApiUtilities.ForemanApiWrapper import ForemanApiWrapper
from ForemanApiWrapper.ApiStateEnforcer.ApiStateEnforcer import ApiStateEnforcer
from ForemanApiWrapper.ApiStateEnforcer.RecordModificationReceipt import RecordModificationReceipt

class Test_ApiStateEnforcer(TestCase):

    def __init__(self, *args, **kwargs):
        super(Test_ApiStateEnforcer, self).__init__(*args, **kwargs)
        self.username = "admin"
        self.password = "password"
        self.url = "https://15.4.5.1"
        self.verifySsl = False
        self.api_wrapper = ForemanApiWrapper(self.username, self.password, self.url, self.verifySsl)
        self.api_state_enforcer = ApiStateEnforcer(self.api_wrapper)


    def test_ensure_state_exists_create_record(self):

        record_name = "some_environment"
        record_type = "environment"
        minimal_record = {
            record_type :{
                "name": record_name
            }
        }
        desired_state = "present"

        try:

            with self.assertRaises(Exception) as e:
                 self.api_state_enforcer.ReadRecord(record_type, minimal_record)

            modification_receipt = self.api_state_enforcer.ensure_state(desired_state, minimal_record)

            self.assertIsNotNone(modification_receipt)
            self.assertEqual(type(modification_receipt), RecordModificationReceipt)
            self.assertTrue(modification_receipt.changed)

        finally:
            self.api_state_enforcer.ensure_state("absent", minimal_record)

        def test_ensure_state_noes_not_exist(self):
            record_name = "some_environment"
            record_type = "environment"
            minimal_record = {
                record_type: {
                    "name": record_name
                }
            }
            desired_state = "absent"

            actual_record_state = self.api_state_enforcer.ensure_state(desired_state, minimal_record)

            self.assertIsNotNone(actual_record_state)
            self.assertEqual(type(actual_record_state), dict)

            minimalStateExists = self.api_state_enforcer.ensure_state(desired_state, minimal_record)

            self.assertTrue(minimalStateExists)

    def test_ensure_state_exists_record_exists(self):

        record_name = "some_environment"
        record_type = "environment"
        minimal_record = {
            record_type: {
                "name": record_name
            }
        }
        desired_state = "present"

        try:

            with self.assertRaises(Exception) as e:
                actual_record_state = self.api_state_enforcer.ReadRecord(record_type, minimal_record)

            modification_receipt = self.api_state_enforcer.ensure_state(desired_state, minimal_record)

            modification_receipt = self.api_state_enforcer.ensure_state(desired_state, minimal_record)

            self.assertIsNotNone(modification_receipt)
            self.assertEqual(type(modification_receipt), RecordModificationReceipt)
            self.assertFalse(modification_receipt.changed)

        finally:
            self.api_state_enforcer.ensure_state( "absent", minimal_record)

    def test__determine_change_required(self):

        actual_record = {
            "subnet": {
                "boot_mode": "DHCP",
                "cidr": 8,
                "created_at": "2020-11-15 06:55:52 UTC",
                "description": None,
                "dhcp": {
                    "id": 1,
                    "name": "foreman.foobar.com",
                    "url": "https://foreman.foobar.com:8443",
                },
                "dhcp_id": 1,
                "dhcp_name": "foreman.foobar.com",
                "dns": {
                    "id": 1,
                    "name": "foreman.foobar.com",
                    "url": "https://foreman.foobar.com:8443",
                },
                "dns_id": 1,
                "dns_primary": "15.4.5.1",
                "dns_secondary": "15.1.1.1",
                "externalipam": None,
                "externalipam_id": None,
                "externalipam_name": None,
                "from": None,
                "gateway": "15.1.1.1",
                "httpboot": None,
                "httpboot_id": None,
                "httpboot_name": None,
                "id": 1,
                "ipam": "None",
                "mask": "255.0.0.0",
                "mtu": 1500,
                "name": "PxeSubnet",
                "network": "15.0.0.0",
                "network_address": "15.0.0.0/8",
                "network_type": "IPv4",
                "priority": None,
                "template": None,
                "template_id": None,
                "template_name": None,
                "tftp": {
                    "id": 1,
                    "name": "foreman.foobar.com",
                    "url": "https://foreman.foobar.com:8443",
                },
                "tftp_id": 1,
                "tftp_name": "foreman.foobar.com",
                "to": None,
                "updated_at": "2020-11-15 06:55:52 UTC",
                "vlanid": None
            }
        }

        minimal_record = {
                "subnet": {
                    "boot_mode": "DHCP",
                    "dhcp_id": "1",
                    "dns_id": "1",
                    "dns_primary": "15.4.5.1",
                    "dns_secondary": "15.1.1.1",
                    "domain_ids": [
                        "2",
                    ],
                    "gateway": "15.1.1.1",
                    "mask": "255.0.0.0",
                    "name": "PxeSubnet",
                    "network": "15.0.0.0",
                    "tftp_id": "1"
                }
            }

        desired_state = "present"
        faw = ForemanApiWrapper
        ase = ApiStateEnforcer(faw)
        change_required, reason =ase._determine_change_required(desired_state, minimal_record, actual_record)

        s = ""

