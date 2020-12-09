import logging
from unittest import TestCase
from ForemanApiWrapper.ForemanApiUtilities.ForemanApiWrapper import ForemanApiWrapper
from ForemanApiWrapper.RecordUtilities import RecordComparison

# Configure logging format and level
logFormat = '%(asctime)s,%(msecs)d %(levelname)-8s [%(module)s:%(funcName)s():%(lineno)d] %(message)s'

logging.basicConfig(format=logFormat,
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.DEBUG)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

class Test_ForemanApiWrapper(TestCase):

    def __init__(self, *args, **kwargs):
        super(Test_ForemanApiWrapper, self).__init__(*args, **kwargs)
        self.username = "admin"
        self.password = "password"
        self.url = "https://15.4.5.1"
        self.verifySsl = False
        self.api_wrapper = ForemanApiWrapper(self.username, self.password, self.url, self.verifySsl)

    # Test function naming convention:
    #
    #   test_<class function name>_<test status>_<notes>
    #

    def __cleanup_record(self, minimal_record):
        # Cleanup and delete the record if it was created
        try:
            self.api_wrapper.read_record(minimal_record)
            self.api_wrapper.delete_record(minimal_record)
        except Exception as e:
            pass

