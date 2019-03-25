import requests
import json
import logging
import sys
import os
from requests.auth import HTTPBasicAuth
from ForemanApiUtilities.ForemanApiCallException import ForemanApiCallException
from RecordUtilities import ForemanApiRecord
from ForemanApiUtilities.ModifiedRecordMismatchException import ModifiedRecordMismatchException
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


PY3 = sys.version_info >= (3, 0)


class ForemanApiWrapper:

    _api_call_error_message = "An error occurred while making an API call. The message could not be extracted. Check json results for more details."
    _modified_record_mismatch_message = "The modified record's 'name' or 'id' fields did not match those supplied in the api url."

    @staticmethod
    def _get_api_record_property_name_mappings():

        # This will import and deserialize the json file with the name mappings

        current_file_path = os.path.realpath(__file__)
        current_directory = os.path.dirname(current_file_path)
        mapping_file_directory = os.path.join(current_directory, "MappingFiles")
        mapping_file_path = os.path.join(mapping_file_directory, "ApiRecordPropertyNameMappings.json")

        # Read the json text from the file
        file_text = None
        with open(mapping_file_path, 'r') as mapping_file:
            file_text = mapping_file.read()

        # Deserialize it into an object
        mappings = json.loads(file_text)
        return mappings

    @staticmethod
    def _get_api_record_to_url_suffix_mappings():
        # Most of the records map directly to the api endpoint
        # for example environment record type maps to the /api/environments endpoint
        # Some record types break this model, and we have a mapping file for this

        # Get the path to the mapping file
        current_file_path = os.path.realpath(__file__)
        current_directory = os.path.dirname(current_file_path)
        mapping_file_directory = os.path.join(current_directory, "MappingFiles")
        mapping_file_path = os.path.join(mapping_file_directory, "ApiRecordToUrlSuffixMapping.json")

        # Read the json text from the file
        file_text = None
        with open(mapping_file_path, 'r') as mapping_file:
            file_text = mapping_file.read()

        # Deserialize it into an object
        mappings = json.loads(file_text)

        return mappings

    def __init__(self, username, password, url, verify_ssl):
        self.username = username
        self.password = password
        self.auth = HTTPBasicAuth(username, password)
        self.url = url
        self.verify_ssl = verify_ssl
        self.property_name_mappings = ForemanApiWrapper._get_api_record_property_name_mappings()
        self.url_suffix_mappings = ForemanApiWrapper._get_api_record_to_url_suffix_mappings()

    @staticmethod
    def _get_headers_for_http_method(http_method):

        # Foreman's API specifies that put and post api calls must set the Content-type header
        # If we dont, we will get an exception as follows:
        #       Exception.args[0]:
        #           '415 Client Error: Unsupported Media Type for url: https://15.4.7.1/api/environments'
        #
        #       response._content:
        #           b'{\n  "error": {"message":"\'Content-Type: \' is unsupported in API v2 for POST and PUT requests. Please use \'Content-Type: application/json\'."}\n}\n'

        headers = {}
        if http_method.lower() in ["put", "post"]:
            headers = {'Content-type': 'application/json', "charset": "utf-8"}

        return headers

    def make_api_call(self, api_endpoint, http_method, arguments=None, headers=None):

        results = None
        try:
            method_name = str.lower(http_method)
            function_pointer = getattr(requests, method_name)
            request_url = self.url + api_endpoint

            if headers is None:
                headers = ForemanApiWrapper._get_headers_for_http_method(http_method)

            logger.debug("Making api call [{0}] {1}".format(http_method.upper(), request_url))

            if arguments:
                logger.debug("Json body:")
                pretty_json = json.dumps(arguments, sort_keys=True, indent=4)
                for line in pretty_json.split("\n"):
                    logger.debug(line)

            results = None
            if arguments:
                results = function_pointer(request_url, auth=self.auth, verify=self.verify_ssl, json=arguments, headers=headers)
            else:
                results = function_pointer(request_url, auth=self.auth, verify=self.verify_ssl)

            # Raise an exception if we did not get a 200 response
            results.raise_for_status()

            # Convert the response to an object
            json_string = results.content.decode("utf-8")
            obj = json.loads(json_string)

            return obj
        except Exception as e:

            # An exception can be raised in several ways
            # In some cases, a non 200 response may return a result object
            # The result may contain json representation of an error

            msg = None
            try:
                json_string = results.content.decode("utf-8")
                result_obj = json.loads(json_string)
                error = result_obj['error']
                if "full_messages" in error.keys():
                    msg = error["full_messages"][0]
                if "message" in error.keys():
                    msg = error["message"]
            except:
                pass

            if not msg:
                msg = ForemanApiWrapper._api_call_error_message

            ex = ForemanApiCallException(
                    msg,
                    api_endpoint,
                    http_method,
                    results,
                    arguments,
                    headers)

            if PY3:
                raise ex from e
            else:
                from future.utils import raise_from
                raise_from(ex, e)

    @staticmethod
    def _format_name_or_id_for_api_url(name_or_id, name_or_id_value):
        endpoint = name_or_id_value
        if name_or_id == "id":
            endpoint = ":{0}".format(name_or_id_value)
        return endpoint

    @staticmethod
    def _get_api_url_suffix_for_record_type(record_type, url_suffix_mappings):
        # Most of the records map directly to the api endpoint
        # for example environment record type maps to the /api/environments endpoint
        # Some record types break this model, and we have a mapping file for this

        # Set the default endpoint
        endpoint_suffix = "{0}s".format(record_type)

        # Check if the record type is contained in the mapping
        # If it is, override the default endpoint
        if record_type in url_suffix_mappings.keys():
            endpoint_suffix = url_suffix_mappings[record_type]

        return endpoint_suffix

    def read_record(self, record_type, minimal_record):

        # This function will check if a record exists by querying the foreman api
        # If the record exists, it will return the json returned by the server
        # If the record does not exist, an error will be raised
        try:
            name_or_id, name_or_id_value = ForemanApiRecord.get_name_or_id_from_record(minimal_record)
            name_or_id_for_url = ForemanApiWrapper._format_name_or_id_for_api_url(name_or_id, name_or_id_value)
            endpoint_suffix = ForemanApiWrapper._get_api_url_suffix_for_record_type(record_type, self.url_suffix_mappings)
            check_url = "/api/{0}/{1}".format(endpoint_suffix, name_or_id_for_url)
            http_method = "GET"
            record_state = self.make_api_call(check_url, http_method)
            return record_state
        except Exception as e:
            raise Exception("An error occurred while reading the record.") from e

    @staticmethod
    def _convert_record_for_api_method(http_method, record_type, record, property_name_mappings):

        # Sometimes this method is used in conjunction with the Check method
        # This is problematic:
        #   The check method uses a GET while the update method uses a PUT
        #   The API is inconsistent in the way it represents records and we know
        #   that the record returned by a GET will not always be the same as a PUT
        #   We may need to change some of the names of the properties on the
        #   json object being submitted to the foreman API
        #   These changes are noted in the mapping file
        # An example mapping is as follows:
        # {
        # 	"put" : {
        # 		"subnet" : {
        # 			"domains" : "domain_ids"
        # 		}
        # 	}
        # }

        # If no mapping is defined, we just return the record untouched
        http_method = http_method.lower()
        record_type = record_type.lower()
        if http_method not in property_name_mappings.keys():
            return record
        if record_type not in property_name_mappings[http_method].keys():
            return record

        required_changes = property_name_mappings[http_method][record_type]

        # For each property in the record, make the required changes
        converted_record = {}
        for key, value in record.items():
            if key in required_changes.keys():
                new_key = required_changes[key]
                converted_record[new_key] = value
            else:
                converted_record[key] = value

        return converted_record

    @staticmethod
    def _get_api_call_arguments(record_type, record):
        # In some cases, the Foreman API expects a json payload to be
        # supplied for the API call

        api_call_arguments = {
            record_type: record
        }
        return api_call_arguments

    def create_record(self, record_type, minimal_record):

        try:
            name_or_id, name_or_id_value = ForemanApiRecord.get_name_or_id_from_record(minimal_record)
            endpoint_suffix = ForemanApiWrapper._get_api_url_suffix_for_record_type(record_type, self.url_suffix_mappings)
            set_url = "/api/{0}".format(endpoint_suffix)
            http_method = "POST"

            headers = ForemanApiWrapper._get_headers_for_http_method(http_method)

            # We may need to convert the record based on the API endpoint being used
            # The API is inconsistent in the way it represents data
            record_for_post = ForemanApiWrapper._convert_record_for_api_method(http_method, record_type, minimal_record, self.property_name_mappings)

            # The api call will expect the arguments in a certain form
            api_call_arguments = ForemanApiWrapper._get_api_call_arguments(record_type, record_for_post)

            record = self.make_api_call(set_url, http_method, api_call_arguments, headers)
            # When a record is created/updated, the record is returned as the result of the api call
            # We will need to verify that the record being returned corresponds to the record in question
            record_match = ForemanApiRecord.confirm_modified_record_identity(name_or_id_value, record)

            if not record_match:
                raise ModifiedRecordMismatchException(
                    self._modified_record_mismatch_message,
                    set_url, http_method,
                    minimal_record,
                    record)

            return record

        except Exception as e:
            raise Exception("An error occurred while creating the record.") from e

    def update_record(self, record_type, minimal_record):

        try:
            name_or_id, name_or_id_value = ForemanApiRecord.get_name_or_id_from_record(minimal_record)
            name_or_id_for_url = ForemanApiWrapper._format_name_or_id_for_api_url(name_or_id, name_or_id_value)
            endpoint_suffix = ForemanApiWrapper._get_api_url_suffix_for_record_type(record_type, self.url_suffix_mappings)
            set_url = "/api/{0}/{1}".format(endpoint_suffix, name_or_id_for_url)
            http_method = "PUT"

            # Foreman's API specifies that put and post api calls must set the Content-type header
            # If we dont, we will get an exception as follows:
            #       Exception.args[0]:
            #           '415 Client Error: Unsupported Media Type for url: https://15.4.7.1/api/environments'
            #
            #       response._content:
            #           b'{\n  "error": {"message":"\'Content-Type: \' is unsupported in API v2 for POST and PUT requests. Please use \'Content-Type: application/json\'."}\n}\n'

            headers = ForemanApiWrapper._get_headers_for_http_method(http_method)

            # We may need to convert the record based on the API endpoint being used
            # The API is inconsistent in the way it represents data
            record_for_put = ForemanApiWrapper._convert_record_for_api_method(http_method, record_type, minimal_record)

            # The api call will expect the arguments in a certain form
            api_call_arguments = ForemanApiWrapper._get_api_call_arguments(record_type, record_for_put)
            record_from_put = self.make_api_call(set_url, http_method, api_call_arguments, headers)

            # We will need to verify that the record being returned corresponds to the record in question
            # We can do this by comparing the nome or id fields on the record returned with
            # The name or id supplied to the API
            record_match = ForemanApiRecord.confirm_modified_record_identity(name_or_id_value, record_from_put)

            if not record_match:
                raise ModifiedRecordMismatchException(
                    self._modified_record_mismatch_message,
                    set_url,
                    http_method,
                    minimal_record,
                    record_from_put)

            return record_from_put

        except Exception as e:
            raise Exception("An error occurred while updating the record.") from e

    def delete_record(self, record_type, minimal_record):

        # It looks like a delete is simply setting some value to nothing
        # Once deleted, a record for the deleted element will be returned
        # This slightly changes things from the Set() function of this class
        # Here, our delete function will delete the record and then ensure
        # that the deleted record matches the url supplied

        try:
            name_or_id, name_or_id_value = ForemanApiRecord.get_name_or_id_from_record(minimal_record)
            name_or_id_for_url = ForemanApiWrapper._format_name_or_id_for_api_url(name_or_id, name_or_id_value)
            endpoint_suffix = ForemanApiWrapper._get_api_url_suffix_for_record_type(record_type, self.url_suffix_mappings)
            delete_url = "/api/{0}/{1}".format(endpoint_suffix, name_or_id_for_url)
            http_method = "DELETE"

            record = self.make_api_call(delete_url, http_method, minimal_record, None)

            # When a record is created/updated, the record is returned as the result of the api call
            # We will need to verify that the record being returned corresponds to the record in question

            # In the case of the delete, the name/id is stored as the suffix in the url
            name_or_id = delete_url.split("/")[-1]
            record_match = ForemanApiRecord.confirm_modified_record_identity(name_or_id_value, record)

            if not record_match:
                raise ModifiedRecordMismatchException(
                    self._modified_record_mismatch_message,
                    delete_url,
                    http_method,
                    minimal_record,
                    record)

            return record

        except Exception as e:
            raise Exception("An error occurred while deleting the record.") from e
