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

