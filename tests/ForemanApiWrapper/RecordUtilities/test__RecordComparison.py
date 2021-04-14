from unittest import TestCase
from ForemanApiWrapper.RecordUtilities import RecordComparison


class Test_RecordComparison(TestCase):

    def test__normalize_record_properties_for_http_method__subnet(self):
        record =  {
            "subnet": {
                "domains": [
                    {
                        "id": 15,
                        "name": "test.foobar.com"
                    }
                ]
            }
        }

        normalized_record = RecordComparison.normalize_record_properties_for_http_method(record)

        expected_record = {
            "subnet": {
                "domain_ids": [15]
            }
        }

        self.assertEqual(expected_record, normalized_record)

    def test__compare_objects__subnet__domain_ids_different_simple(self):
        record_a = {
            "subnet": {
                "domains": [
                    {
                        "id": 15,
                        "name": "test.foobar.com"
                    }
                ]
            }
        }
        record_b = {
            "subnet": {
                "domain_ids": []
            }
        }
        match, reason = RecordComparison.compare_records(record_b, record_a)
        self.assertFalse(match)

    def test__compare_objects__subnet__domain_ids_different(self):
        record_a = {
            "subnet": {
                "bmc": None,
                "bmc_id": None,
                "bmc_name": None,
                "boot_mode": "DHCP",
                "cidr": 8,
                "created_at": "2021-04-13 23:44:11 UTC",
                "description": None,
                "dhcp": {
                    "id": 1,
                    "name": "foreman.foobar.com",
                    "url": "https://foreman.foobar.com:8443"
                },
                "dhcp_id": 1,
                "dhcp_name": "foreman.foobar.com",
                "dns": {
                    "id": 1,
                    "name": "foreman.foobar.com",
                    "url": "https://foreman.foobar.com:8443"
                },
                "dns_id": 1,
                "dns_primary": "15.4.5.1",
                "dns_secondary": "15.1.1.1",
                "domains": [
                    {
                        "id": 15,
                        "name": "test.foobar.com"
                    }
                ],
                "externalipam": None,
                "externalipam_id": None,
                "externalipam_name": None,
                "from": None,
                "gateway": "15.1.1.1",
                "httpboot": None,
                "httpboot_id": None,
                "httpboot_name": None,
                "id": 4,
                "interfaces": [],
                "ipam": "None",
                "locations": [
                    {
                        "description": None,
                        "id": 2,
                        "name": "Default Location",
                        "title": "Default Location"
                    }
                ],
                "mask": "255.0.0.0",
                "mtu": 1500,
                "name": "Modified Subnet",
                "network": "15.0.0.0",
                "network_address": "15.0.0.0/8",
                "network_type": "IPv4",
                "nic_delay": None,
                "organizations": [
                    {
                        "description": None,
                        "id": 1,
                        "name": "Default Organization",
                        "title": "Default Organization"
                    }
                ],
                "parameters": [],
                "priority": None,
                "template": None,
                "template_id": None,
                "template_name": None,
                "tftp": {
                    "id": 1,
                    "name": "foreman.foobar.com",
                    "url": "https://foreman.foobar.com:8443"
                },
                "tftp_id": 1,
                "tftp_name": "foreman.foobar.com",
                "to": None,
                "updated_at": "2021-04-13 23:44:11 UTC",
                "vlanid": None
            }
        }
        record_b = {
            "subnet": {
                "boot_mode": "DHCP",
                "dhcp_id": 1,
                "dns_id": 1,
                "dns_primary": "15.4.5.1",
                "dns_secondary": "15.1.1.1",
                "domain_ids": [],
                "gateway": "15.1.1.1",
                "mask": "255.0.0.0",
                "name": "Modified Subnet",
                "network": "15.0.0.0",
                "tftp_id": 1
            }
        }
        match, reason = RecordComparison.compare_records(record_b, record_a)
        self.assertFalse(match)
