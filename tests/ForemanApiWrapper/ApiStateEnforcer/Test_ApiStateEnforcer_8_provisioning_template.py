from tests.ForemanApiWrapper.ApiStateEnforcer.Test_ApiStateEnforcer import Test_ApiStateEnforcer
from tests.ForemanApiWrapper.ApiStateEnforcer.Test_ApiStateEnforcer_1_smartproxy import Test_ApiStateEnforcer_1_smartproxy
from tests.ForemanApiWrapper.ApiStateEnforcer.Test_ApiStateEnforcer_2_domain import Test_ApiStateEnforcer_2_domain
from tests.ForemanApiWrapper.ApiStateEnforcer.Test_ApiStateEnforcer_3_subnet import Test_ApiStateEnforcer_3_subnet
from tests.ForemanApiWrapper.ApiStateEnforcer.Test_ApiStateEnforcer_4_architecture import Test_ApiStateEnforcer_4_architecture
from tests.ForemanApiWrapper.ApiStateEnforcer.Test_ApiStateEnforcer_5_medium import Test_ApiStateEnforcer_5_medium
from tests.ForemanApiWrapper.ApiStateEnforcer.Test_ApiStateEnforcer_6_operatingsystem import Test_ApiStateEnforcer_6_operatingsystem
from tests.ForemanApiWrapper.ApiStateEnforcer.Test_ApiStateEnforcer_7_ptable import Test_ApiStateEnforcer_7_ptable


import logging

# Configure logging format and level
logFormat = '%(asctime)s,%(msecs)d %(levelname)-8s [%(module)s:%(funcName)s():%(lineno)d] %(message)s'

logging.basicConfig(format=logFormat,
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.DEBUG)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

class Test_ApiStateEnforcer_8_provisioning_template(Test_ApiStateEnforcer):

    def __init__(self, *args, **kwargs):
        super(Test_ApiStateEnforcer_8_provisioning_template, self).__init__(*args, **kwargs)

    @staticmethod
    def __minimal_record():

        return {
            "provisioning_template": {
                "audit_comment": "",
                "locked": False,
                "name": "CentOS 7.9.2009 PXELinux Template",
                "operatingsystem_ids": [
                    "1"
                ],
                "snippet": False,
                "template": "<%#\nkind: PXELinux\nname: Kickstart default PXELinux\nmodel: ProvisioningTemplate\noses:\n- CentOS\n- Fedora\n- RedHat\n-%>\n# This file was deployed via '<%= template_name %>' template\n\n<%\n  major = @host.operatingsystem.major.to_i\n  mac = @host.provision_interface.mac\n\n  # Tell Anaconda to perform network functions with boot interface\n  #  both current and legacy syntax provided\n  options = [\"network\", \"ksdevice=bootif\", \"ks.device=bootif\"]\n  if mac\n    bootif = '00-' + mac.gsub(':', '-')\n    options.push(\"BOOTIF=#{bootif}\")\n  end\n\n  # Tell anaconda the location of the installation program runtime image\n  options.push(\"inst.stage2=\" + @mediapath.split(\" \")[-1])\n\n  # Tell Anaconda what to pass off to kickstart server\n  #  both current and legacy syntax provided\n  options.push(\"kssendmac\", \"ks.sendmac\", \"inst.ks.sendmac\")\n\n  # handle non-DHCP environments (e.g. bootdisk)\n  subnet = @host.provision_interface.subnet\n  unless subnet.dhcp_boot_mode?\n    # static network configuration\n    ip = @host.provision_interface.ip\n    mask = subnet.mask\n    gw = subnet.gateway\n    dns = [subnet.dns_primary]\n    if subnet.dns_secondary != ''\n      dns.push(subnet.dns_secondary)\n    end\n    if (@host.operatingsystem.name.match(/Fedora/i) && major < 17) || major < 7\n      # old Anacoda found in Fedora 16 or RHEL 6 and older\n      dns_servers = dns.join(',')\n      options.push(\"ip=#{ip}\", \"netmask=#{mask}\", \"gateway=#{gw}\", \"dns=#{dns_servers}\")\n    else\n      options.push(\"ip=#{ip}::#{gw}:#{mask}:::none\")\n      dns.each { |server|\n        options.push(\"nameserver=#{server}\")\n      }\n    end\n  end\n\n  ksoptions = options.join(' ')\n  timeout = host_param('loader_timeout').to_i * 10\n  timeout = 100 if timeout.nil? || timeout <= 0\n-%>\n\nDEFAULT menu\nMENU TITLE Booting into OS installer (ESC to stop)\nTIMEOUT <%= timeout %>\nONTIMEOUT installer\n\nLABEL installer\n  MENU LABEL <%= template_name %>\n  KERNEL <%= @kernel %>\n  APPEND initrd=<%= @initrd %> inst.ks=<%= foreman_url('provision') %> <%= pxe_kernel_options %> <%= ksoptions %>\n  IPAPPEND 2",
                "template_kind_id": 1
            }
        }

    @staticmethod
    def _create_provisioning_template(api_state_enforcer):
        desired_state = "present"
        minimal_record = Test_ApiStateEnforcer_8_provisioning_template.__minimal_record()
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
        Test_ApiStateEnforcer_8_provisioning_template._create_provisioning_template(self.api_state_enforcer)
        # Ensure State
        desired_state = "present"
        minimal_record = Test_ApiStateEnforcer_8_provisioning_template.__minimal_record()
        modification_receipt = self.api_state_enforcer.ensure_state(desired_state, minimal_record)
        self.assertFalse(modification_receipt.changed)

    def test__ptable__update(self):
        self.fail("Not implemented")

    def test__ptable__delete(self):
        self.fail("Not implemented")