import requests
import json
import logging
import sys
import os
from requests.auth import HTTPBasicAuth
from ForemanApiWrapper.ForemanApiUtilities.ForemanApiCallException import ForemanApiCallException
from ForemanApiWrapper.RecordUtilities import ForemanApiRecord
from ForemanApiWrapper.ForemanApiUtilities.ModifiedRecordMismatchException import ModifiedRecordMismatchException


logger = logging.getLogger()


PY3 = sys.version_info >= (3, 0)


if PY3:
    import urllib.parse
else:
    import urllib


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

    @staticmethod
    def _get_api_record_property_identification_property_mappings():
        # Most endpoints use the id or name field to identify a particular record
        # In some cases, the endpoint has not been implemented to allow this
        # This mapping file will keep track of which record types use what identifiers

        # Get the path to the mapping file
        current_file_path = os.path.realpath(__file__)
        current_directory = os.path.dirname(current_file_path)
        mapping_file_directory = os.path.join(current_directory, "MappingFiles")
        mapping_file_path = os.path.join(mapping_file_directory, "ApiRecordIdentificationPropertyMappings.json")

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
        self.record_identification_mappings = ForemanApiWrapper._get_api_record_property_identification_property_mappings()

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

            if arguments:
                logger.debug("Json body:")
                pretty_json = json.dumps(arguments, sort_keys=True, indent=4)
                for line in pretty_json.split("\n"):
                    logger.debug(line)

            logger.debug("Making api call [{0}] {1}".format(http_method.upper(), request_url))

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
    def _determine_record_suffix(record, url_suffix_mappings):

        try:
            record_type = ForemanApiRecord.get_record_type_from_record(record)

            # Most of the records map directly to the api endpoint
            # for example environment record type maps to the /api/environments endpoint
            # Set the default endpoint
            endpoint_suffix = "/{0}s".format(record_type)

            # Some record types break this model, and we have a mapping file for this
            # For example the medium record maps to the media endpoint
            # Check if the record type is contained in the mapping
            # If it is, override the default endpoint
            if record_type in url_suffix_mappings.keys():
                endpoint_suffix = "/{0}".format(url_suffix_mappings[record_type])

            # Some records are even more complicated and require information from other records
            # For example the os_default_templates record url suffix relies on the operating_system record id
            # These records are specified with respect to another record
            # This information is stored in the dependencies property of the AnsibleForemanModule
            # If the task has specified dependencies we will build the url dynamically
            # The url should resemble the following when complete:
            #       https://15.4.7.1/api/operatingsystems/19/os_default_templates?search=provisioning_template_id%20110
            #The suffix should look like this:
            #       https://15.4.7.1/api/operatingsystems/19/os_default_templates
            record_dependencies = ForemanApiRecord.get_record_dependencies(record)
            if record_dependencies:
                tmp_suffix = ""

                for x in range(0, len(record_dependencies)):
                    record_dependency = record_dependencies[x]
                    id = ForemanApiRecord.get_id_from_record(record_dependency)
                    dependency_suffix = ForemanApiWrapper._determine_record_suffix(record_dependency, url_suffix_mappings)
                    tmp_suffix += "{0}/{1}".format(dependency_suffix, id)

                endpoint_suffix = "{0}{1}".format(tmp_suffix, endpoint_suffix)

            return endpoint_suffix
        except Exception as e:
            raise Exception("An error occurred while determining the url suffix for the record.") from e

    @staticmethod
    def _determine_property_key_and_value_for_query_string(record, record_identification_mappings):

        try:
            record_body = ForemanApiRecord.get_record_body_from_record(record)
            # If the record has an id we will use that as it is the most exact match
            if "id" in record_body.keys():
                return "id", record_body["id"]
            # If there is no id, we will need to use an alternate property as a search criteria
            # AFAIK any property on the record should work in a query string
            else:
                record_type = ForemanApiRecord.get_record_type_from_record(record)

                # We have the record_identification_mappings as a way to specify a preferred search field
                # We will try to use this mapping first
                possible_keys = []
                if record_type in record_identification_mappings.keys():
                    possible_keys = record_identification_mappings[record_type]
                    if "id" in possible_keys:
                        possible_keys.remove("id")

                # Choose a key from the list of possible keys and use that for the query
                query_key = None
                for possible_key in possible_keys:
                    if possible_key in record_body.keys():
                        query_key = possible_keys[0]
                        break

                # If the preferred keys are not found, use another field that is on the record
                if query_key is None:
                    for possible_key in record_body.keys():
                        possible_value = record_body[possible_key]
                        if type(possible_key) == str:
                            query_key = possible_key
                            break

                # If we could not find any keys for the query... throw an exception
                if query_key is None:
                    raise Exception("The record did not contain any properties which could be used in a query string.")

                query_value = record_body[query_key]

                return query_key, query_value
        except Exception as e:
            raise Exception("An error occured while determining key and value for query string.") from e

    @staticmethod
    def _determine_record_query_string(record, record_identification_mappings):

        try:
                query_key, query_value = ForemanApiWrapper._determine_property_key_and_value_for_query_string(record, record_identification_mappings)

                # Create the query string
                query = ""
                if query_key == "id":
                    query = "/{0}".format(query_value)
                else:
                    query_string = "{0}=\"{1}\"".format(query_key, query_value)

                    # Encode the query string for url
                    encoded_query_string = None
                    if PY3:
                        encoded_query_string = urllib.parse.quote(query_string)
                    else:
                        encoded_query_string = urllib.quote(query_string)
                    query = "?search={0}".format(encoded_query_string)

                return query
        except Exception as e:
            raise Exception("An error occured while determining query string for api url.") from e

    @staticmethod
    def _determine_api_endpoint_for_record(record, url_suffix_mappings, record_identification_mapping, include_query=True):

        # An example url is as follows
        #   https://15.4.7.1/api/operatingsystems/19
        #
        # An example of a url which requires a query
        #   https://15.4.7.1/api/operatingsystems/19/os_default_templates?search=provisioning_template_id%20110
        #
        # We will break down the formation of the url as follows:
        #   [ api _ prefix    ]/api/[   record_suffix                                                  ][   query string                                            ]
        #   [ api_url                                                                                                                                                                    ]
        #

        try:
            api_suffix = ForemanApiWrapper._determine_record_suffix(record, url_suffix_mappings)
            query_string = ForemanApiWrapper._determine_record_query_string(record, record_identification_mapping)
            api_endpoint = "/api{0}".format(api_suffix)
            if include_query:
                api_endpoint = "{0}{1}".format(api_endpoint, query_string)
            return api_endpoint
        except Exception as e:
            raise Exception("An error occurred while determine the api endpoint for the specified record.")

    def read_record(self, minimal_record):

        # This function will check if a record exists by querying the foreman api
        # If the record exists, it will return the json returned by the server
        # If the record does not exist, an error will be raised
        try:

            check_url = self._determine_api_endpoint_for_record(minimal_record, self.url_suffix_mappings, self.record_identification_mappings)
            http_method = "GET"
            record_type = ForemanApiRecord.get_record_type_from_record(minimal_record)
            results = self.make_api_call(check_url, http_method)

            # If a single record is returned, return it
            record_body = None
            if "results" not in results.keys():
                record_body = results
            # If a result set contains a single item, return it
            else:
                if len(results["results"]) == 0:
                    logger.debug("Empty result set returned by the api.")
                    return None
                else:
                    if len(results["results"]) > 1:
                        logger.debug("There were '{0}' records returned when there should have only been one.".format(len(results["results"]) ))
                        logger.debug("Using extra query logic to determine if the record was found.")

                    # Sometimes the API will lie and give us records which do not match the query string
                    # For exmpale, If I GET the following url
                    #   https://15.4.7.1/api/operatingsystems/29/os_default_templates?search=provisioning_template_id%3D161
                    # I will get back records who's provisioning_tepmlate_id do not equal 161
                    # We will have to implement our own query logic to weed out the bad results
                    # Basically we will check if the query key matches the value

                    records = []
                    query_key, query_value = ForemanApiWrapper._determine_property_key_and_value_for_query_string(minimal_record, self.record_identification_mappings)
                    for tmp_record_body in results["results"]:
                        # Create a tmp record to compare with the minimal record
                        tmp_record = {record_type: tmp_record_body}
                        # Check f the query key exists in both objects, and the values are the same
                        a = query_key not in minimal_record[record_type].keys()
                        b = query_key not in tmp_record[record_type].keys()
                        c = minimal_record[record_type][query_key] != tmp_record[record_type][query_key]
                        # If a record satisfies the query, append it
                        if not (a or b or c):
                            records.append(tmp_record)

                    # Multiple records should not occur as a result of the query
                    # If they do, we should throw an exception
                    if len(records) != 1:
                        err_str = "There were '{0}' records returned from the query when there should have only been one."
                        err_str += "Custom logic was not able to filter the results to a single record"
                        err_str = err_str.format(len(records))
                        raise ForemanApiCallException(
                            err_str,
                            check_url,
                            http_method,
                            results,
                            None,
                            None)

                    record_body = records[0][record_type]

            record = {record_type: record_body}

            return record
        except Exception as e:
            raise Exception("An error occurred while reading the record.") from e

    @staticmethod
    def _convert_record_for_api_method(http_method, record, property_name_mappings):

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

        http_method = http_method.lower()

        # If no mapping is defined, we just return the record untouched
        record_type = ForemanApiRecord.get_record_type_from_record(record)
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
    def _get_api_call_arguments(record):
        # In some cases, the Foreman API expects a json payload to be
        # supplied for the API call
        # We have added our own "dependencies" property to the record which will need to be remove
        if "dependencies" in record.keys():
            record.pop("dependencies")
        return record

    def create_record(self, minimal_record):

        try:
            set_url = self._determine_api_endpoint_for_record(minimal_record, self.url_suffix_mappings, self.record_identification_mappings, include_query=False)
            http_method = "POST"

            headers = ForemanApiWrapper._get_headers_for_http_method(http_method)

            # We may need to convert the record based on the API endpoint being used
            # The API is inconsistent in the way it represents data
            record_for_post = ForemanApiWrapper._convert_record_for_api_method(http_method, minimal_record, self.property_name_mappings)

            # The api call will expect the arguments in a certain form
            api_call_arguments = ForemanApiWrapper._get_api_call_arguments(record_for_post)
            record_type = ForemanApiRecord.get_record_type_from_record(minimal_record)
            created_record_body = self.make_api_call(set_url, http_method, api_call_arguments, headers)
            created_record = {record_type : created_record_body}

            return created_record

        except Exception as e:
            raise Exception("An error occurred while creating the record.") from e

    def update_record(self, minimal_record):

        try:
            set_url = self._determine_api_endpoint_for_record(minimal_record, self.url_suffix_mappings, self.record_identification_mappings)
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
            record_for_put = ForemanApiWrapper._convert_record_for_api_method(http_method, minimal_record, self.property_name_mappings)

            # The api call will expect the arguments in a certain form
            api_call_arguments = ForemanApiWrapper._get_api_call_arguments(record_for_put)
            record_type = ForemanApiRecord.get_record_type_from_record(minimal_record)
            updated_record_body = self.make_api_call(set_url, http_method, api_call_arguments, headers)
            updated_record = {record_type : updated_record_body}

            # Verify that the updated record has the same id as the minimal record
            # Raise an exception if it does not
            try:
                record_name_or_id = ForemanApiRecord.get_name_or_id_from_record(minimal_record)
                record_name_or_id_value = record_name_or_id[1]
                ForemanApiRecord.confirm_modified_record_identity(record_name_or_id_value, record_type, updated_record)
            except Exception as e:
                raise ModifiedRecordMismatchException(
                    self._modified_record_mismatch_message,
                    set_url,
                    http_method,
                    minimal_record,
                    updated_record)

            return updated_record

        except Exception as e:
            raise Exception("An error occurred while updating the record.") from e

    def delete_record(self, minimal_record):

        # It looks like a delete is simply setting some value to nothing
        # Once deleted, a record for the deleted element will be returned
        # This slightly changes things from the Set() function of this class
        # Here, our delete function will delete the record and then ensure
        # that the deleted record matches the url supplied

        try:
            # First we determine the url we will be submitting to
            base_delete_url = self._determine_api_endpoint_for_record(minimal_record, self.url_suffix_mappings, self.record_identification_mappings, include_query=False)
            record_identifier_field, record_identifier = ForemanApiRecord.get_identifier_from_record(minimal_record, self.record_identification_mappings)
            delete_url= "{0}/{1}".format(base_delete_url, record_identifier)

            http_method = "DELETE"

            # We may need to convert the record based on the API endpoint being used
            # The API is inconsistent in the way it represents data
            record_for_delete = ForemanApiWrapper._convert_record_for_api_method(http_method, minimal_record, self.property_name_mappings)

            # The api call will expect the arguments in a certain form
            api_call_arguments = ForemanApiWrapper._get_api_call_arguments(record_for_delete)
            minimal_record_type = ForemanApiRecord.get_record_type_from_record(minimal_record)
            deleted_record_body = self.make_api_call(delete_url, http_method, api_call_arguments, None)
            deleted_record = {
                minimal_record_type: deleted_record_body
            }

            # Verify that the updated record has the same id as the minimal record
            # Raise an exception if it does not
            try:
                ForemanApiRecord.confirm_modified_record_identity(record_identifier, minimal_record_type, deleted_record)
            except Exception as e:
                raise ModifiedRecordMismatchException(
                    self._modified_record_mismatch_message,
                    delete_url,
                    http_method,
                    minimal_record,
                    deleted_record)

            return deleted_record

        except Exception as e:
            raise Exception("An error occurred while deleting the record.") from e
