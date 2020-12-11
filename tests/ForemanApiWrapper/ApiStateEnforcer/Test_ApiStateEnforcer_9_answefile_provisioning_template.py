from tests.ForemanApiWrapper.ApiStateEnforcer.Test_ApiStateEnforcer import Test_ApiStateEnforcer
from tests.ForemanApiWrapper.ApiStateEnforcer.Test_ApiStateEnforcer_1_smartproxy import Test_ApiStateEnforcer_1_smartproxy
from tests.ForemanApiWrapper.ApiStateEnforcer.Test_ApiStateEnforcer_2_domain import Test_ApiStateEnforcer_2_domain
from tests.ForemanApiWrapper.ApiStateEnforcer.Test_ApiStateEnforcer_3_subnet import Test_ApiStateEnforcer_3_subnet
from tests.ForemanApiWrapper.ApiStateEnforcer.Test_ApiStateEnforcer_4_architecture import Test_ApiStateEnforcer_4_architecture
from tests.ForemanApiWrapper.ApiStateEnforcer.Test_ApiStateEnforcer_5_medium import Test_ApiStateEnforcer_5_medium
from tests.ForemanApiWrapper.ApiStateEnforcer.Test_ApiStateEnforcer_6_operatingsystem import Test_ApiStateEnforcer_6_operatingsystem
from tests.ForemanApiWrapper.ApiStateEnforcer.Test_ApiStateEnforcer_7_ptable import Test_ApiStateEnforcer_7_ptable
from tests.ForemanApiWrapper.ApiStateEnforcer.Test_ApiStateEnforcer_8_pxelinux_provisioning_template import Test_ApiStateEnforcer_8_pxelinux_provisioning_template

import logging

# Configure logging format and level
logFormat = '%(asctime)s,%(msecs)d %(levelname)-8s [%(module)s:%(funcName)s():%(lineno)d] %(message)s'

logging.basicConfig(format=logFormat,
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.DEBUG)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

class Test_ApiStateEnforcer_9_answerfile_provisioning_template(Test_ApiStateEnforcer):

    def __init__(self, *args, **kwargs):
        super(Test_ApiStateEnforcer_9_answerfile_provisioning_template, self).__init__(*args, **kwargs)

    @staticmethod
    def _minimal_record(operatingsystem_id):

        return {
            "provisioning_template": {
                "audit_comment": "",
                "locked": False,
                "name": "CentOS 7.9.2009 Kickstart Template",
                "operatingsystem_ids": [
                    operatingsystem_id
                ],
                "snippet": False,
                "template": "<%#\nkind: provision\nname: CentOS Kickstart Template\nmodel: ProvisioningTemplate\noses:\n- CentOS\n- Fedora\n- RedHat\n%>\n\n<% if @host.params.has_key?(\"root_disk_serial\") or @host.params.has_key?(\"root_disk_name\") -%>\n# =====================================\n# Pre Section\n# =====================================\n\n# In some cases we want kickstart/anaconda to install on a particular device\n# If this is the case, we will include a %pre section to our file\n# In this section we will execute a script to determine the device name based on some parameters\n# The information will be written to files to be used in %include statements later on\n\n%pre --log /root/pre-install.log\n\n<% if @host.params.has_key?(\"root_disk_serial\") -%>\nset -e\nset -x\n\nDEVICE_FILE=\"/root/device.txt\"\nIGNORE_FILE=\"/root/ignore_command.txt\"\nCLEARPART_FILE=\"/tmp/clearpart.txt\"\n\nSERIAL=\"<%= @host.params['root_disk_serial'] %>\"\n\nDEVICE=$(lsblk -d --output NAME,TYPE,SERIAL| grep -i \"${SERIAL}\" | awk '{print $1}')\n\nif [ -z \"${DEVICE}\" ]; then\n        echo \"No device found for serial number ${SERIAL}\"\n        exit 1\nelse\n        echo \"Found device ${DEVICE}\"\nfi\n\necho \"${DEVICE}\" > ${DEVICE_FILE}\necho \"ignoredisk --only-use=${DEVICE}\" > ${IGNORE_FILE}\necho \"clearpart --all --drives=${DEVICE}\" > ${CLEARPART_FILE}\n\nexit 0\n<% elsif @host.params.has_key?(\"root_disk_name\") -%>\nset -e\nset -x\n\nIGNORE_FILE=\"/root/ignore_command.txt\"\nCLEARPART_FILE=\"/root/clearpart.txt\"\n\nNAME=\"<%= @host.params['root_disk_name'] %>\"\n\nDEVICE=$(lsblk -d --output NAME,TYPE,SERIAL| grep -i \"${NAME}\" | awk '{print $1}')\n\nif [ -z \"${DEVICE}\" ]; then\n        echo \"No device found for ${NAME}\"\n        exit 1\nelse\n        echo \"Found device ${DEVICE}\"\nfi\n\necho \"ignoredisk --only-use=${DEVICE}\" > ${IGNORE_FILE}\necho \"clearpart --all --drives=${DEVICE}\" > ${CLEARPART_FILE}\nexit 0\n<% end -%>\n\n%end\n<% end %>\n\n\n# =====================================\n# Command Section\n# =====================================\n\n# Set system authorization information\nauth --useshadow --passalgo=<%= @host.operatingsystem.password_hash.downcase || 'sha256' %>\n\n# Run the Setup Agent on first boot\nfirstboot --enable\n\n# Keyboard layouts\nkeyboard <%= host_param('keyboard') || 'us' %>\n\n# System language\nlang <%= host_param('lang') || 'en_US.UTF-8' %>\n\n# Configure the network\n<% subnet = @host.subnet -%>\n<% if subnet.respond_to?(:dhcp_boot_mode?) -%>\n<% dhcp = subnet.dhcp_boot_mode? && !@static -%>\n<% else -%>\n<% dhcp = !@static -%>\n<% end -%>\n\n<% # Set a var to help setup the network command %>\n<% os_major = @host.operatingsystem.major.to_i %>\n\nnetwork --bootproto <%= dhcp ? 'dhcp' : \"static --ip=#{@host.ip} --netmask=#{subnet.mask} --gateway=#{subnet.gateway} --nameserver=#{[subnet.dns_primary, subnet.dns_secondary].select{ |item| item.present? }.join(',')} --mtu=#{subnet.mtu.to_s}\" %> --hostname <%= @host %><%= os_major >= 6 ? \" --device=#{@host.mac}\" : '' -%>\n\n# Set the password for the root user\nrootpw --iscrypted <%= root_pass %>\n\n# Set SELinux\nselinux --<%= host_param('selinux-mode') || host_param('selinux') || 'enforcing' %>\n\n# configure the timezone\ntimezone --utc <%= host_param('time-zone') || 'UTC' %>\n\n# Configure the installer to use the media URL\n# Line should look like:\n#    url --url http://15.4.5.1:8081/CentOS/7.8.2003/os/x86_64 \n\n<%= @mediapath %>\n\n<% if not @host.params.has_key?(\"force_build\") %>\n# Set the installer to only run on new installations\nfirstboot --enable\n<% end %>\n\n# Select the hard disk to install to\n<% if @host.params.has_key?(\"root_disk_serial\") %>\n%include /root/ignore_command.txt\n<% elsif  @host.params.has_key?(\"root_disk_name\") %>\nignoredisk --only-use=<%= @host.params['root_disk_name'] %>\n<% else %>\nignoredisk --only-use=sda\n<% end %>\n\n# Use the text display mode\ntext\n\n# Configure the bootloader\nbootloader --location=mbr --append=\"<%= host_param('bootloader-append') || 'nofb quiet splash=quiet' %>\" <%= @grub_pass %>\n\n# Configure the master boot record and decide whether or not to wipe partitions\n<% if @host.params.has_key?(\"force_build\") %>\n# Destory the master boot record label so the disk can be reformatted\nzerombr\n<% if @host.params.has_key?(\"root_disk_serial\") or @host.params.has_key?(\"root_disk_name\") %>\n# Tell the system to delete partitions from a specifc disk so the installation can succeed\n%include /root/clearpart.txt\n<% end %>\n<% else %>\nclearpart --none --initlabel\n<% end %>\n\n# Tell the system to auto partition the install\nautopart --type=lvm\n\n\n# Tell the system to reboot after install complete\nreboot\n\n# =====================================\n# Packages Section\n# =====================================\n\n%packages\n@^minimal\n@core\nchrony\nkexec-tools\n\n%end\n\n# =====================================\n# End Section\n# =====================================\n\n# Configure anaconda to use the kdump addon\n# This will allow the installation to create crash dumps in the event of kernel panic during instllation\n\n%addon com_redhat_kdump --enable --reserve-mb='auto'\n%end\n\n# Execute a post installation command to alert Foreman that the build has completed\n\n%post --log /root/post-install.log\n\nset -e\n\ncurl --insecure <%= foreman_url('built') %> 2>&1\n\n%end",
                "template_kind_id": 5
            }
        }

    @staticmethod
    def _create_answefile_provisioning_template(api_state_enforcer, operatingsystem_id):
        desired_state = "present"
        minimal_record = Test_ApiStateEnforcer_9_answerfile_provisioning_template._minimal_record(operatingsystem_id)
        modification_receipt = api_state_enforcer.ensure_state(desired_state, minimal_record)
        return modification_receipt

    def test__answerfile_provisioning_template__create(self):
        self.fail("Not implemented")

    def test__answerfile_provisioning_template__exists(self):
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
        operatingsystem_id = modification_receipt.actual_record["operatingsystem"]["id"]
        Test_ApiStateEnforcer_7_ptable._create_ptable(self.api_state_enforcer)
        Test_ApiStateEnforcer_8_pxelinux_provisioning_template._create_pxelinux_provisioning_template(self.api_state_enforcer, operatingsystem_id)
        Test_ApiStateEnforcer_9_answerfile_provisioning_template._create_answefile_provisioning_template(self.api_state_enforcer, operatingsystem_id)
        # Ensure State
        desired_state = "present"
        minimal_record = Test_ApiStateEnforcer_8_pxelinux_provisioning_template._minimal_record(operatingsystem_id)
        modification_receipt = self.api_state_enforcer.ensure_state(desired_state, minimal_record)
        self.assertFalse(modification_receipt.changed)

    def test__answerfile_provisioning_template__update(self):
        self.fail("Not implemented")

    def test__answerfile_provisioning_template__delete(self):
        self.fail("Not implemented")