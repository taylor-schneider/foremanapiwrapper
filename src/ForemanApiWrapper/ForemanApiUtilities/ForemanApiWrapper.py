import requests
import json
import logging
import sys
import os
from requests.auth import HTTPBasicAuth
from ForemanApiWrapper.ForemanApiUtilities.ForemanApiCallException import ForemanApiCallException
from ForemanApiWrapper.RecordUtilities import ForemanApiRecord
from ForemanApiWrapper.ForemanApiUtilities.ModifiedRecordMismatchException import ModifiedRecordMismatchException
from ForemanApiWrapper.ForemanApiUtilities.Mappings.ApiRecordIdentificationPropertyMappings import ApiRecordIdentificationPropertyMappings
from ForemanApiWrapper.ForemanApiUtilities.Mappings.ApiRecordPropertyNameMappings import ApiRecordPropertyNameMappings
from ForemanApiWrapper.ForemanApiUtilities.Mappings.ApiRecordToUrlSuffixMapping import ApiRecordToUrlSuffixMapping


logger = logging.getLogger()

PY3 = sys.version_info >= (3, 0)


if PY3:
    import urllib.parse
else:
    import urllib

class ForemanApiWrapper:

    _api_call_error_message = "An error occurred while making an API call. The message could not be extracted. Check json results for more details."
    _modified_record_mismatch_message = "The modified record's 'name' or 'id' fields did not match those supplied in the api url."

    def __init__(self, username, password, url, verify_ssl):
        self.username = username
        self.password = password
        self.auth = HTTPBasicAuth(username, password)
        self.url = url
        self.verify_ssl = verify_ssl

        if not verify_ssl:
            #os.environ["PYTHONWARNINGS"] = "ignore:Unverified HTTPS request"
            import warnings
            from requests.packages.urllib3.exceptions import InsecureRequestWarning
            warnings.simplefilter('ignore', InsecureRequestWarning)

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
    def _determine_record_suffix(record):

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
            if record_type in ApiRecordToUrlSuffixMapping.keys():
                endpoint_suffix = "/{0}".format(ApiRecordToUrlSuffixMapping[record_type])

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
                    dependency_suffix = ForemanApiWrapper._determine_record_suffix(record_dependency)
                    tmp_suffix += "{0}/{1}".format(dependency_suffix, id)

                endpoint_suffix = "{0}{1}".format(tmp_suffix, endpoint_suffix)

            return endpoint_suffix
        except Exception as e:
            raise Exception("An error occurred while determining the url suffix for the record.") from e

    @staticmethod
    def _determine_property_key_and_value_for_query_string(record):

        try:
            record_body = ForemanApiRecord.get_record_body_from_record(record)
            # If the record has an id we will use that as it is the most exact match
            if "id" in record_body.keys():
                return "id", record_body["id"]
            # If there is no id, we will need to use an alternate property as a search criteria
            # AFAIK any property on the record should work in a query string
            else:
                record_type = ForemanApiRecord.get_record_type_from_record(record)

                # We have the ApiRecordIdentificationPropertyMappings as a way to specify a preferred search field
                # We will try to use this mapping first
                possible_keys = []
                if record_type in ApiRecordIdentificationPropertyMappings.keys():
                    possible_keys = ApiRecordIdentificationPropertyMappings[record_type]
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

                # For some reason, the API will convert some fields to lower while others
                # will be left in their original format. For example the mac address field will
                # be converted to lower for the GET but the POST will accept either
                # We will do the conversion
                if query_key in ["mac"]:
                    query_value = query_value.lower()

                return query_key, query_value
        except Exception as e:
            raise Exception("An error occurred while determining key and value for query string.") from e

    @staticmethod
    def _determine_record_query_string(record, uncapitalize_query=False):

        try:
                query_key, query_value = ForemanApiWrapper._determine_property_key_and_value_for_query_string(record)

                if uncapitalize_query:
                   query_value = query_value.lower()

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
    def _determine_api_endpoint_for_record(record, include_query=True):

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
            record_suffix = ForemanApiWrapper._determine_record_suffix(record)
            query_string = ForemanApiWrapper._determine_record_query_string(record)
            api_endpoint = "/api{0}".format(record_suffix)
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

            check_url = self._determine_api_endpoint_for_record(minimal_record)
            http_method = "GET"
            record_type = ForemanApiRecord.get_record_type_from_record(minimal_record)
            results = self.make_api_call(check_url, http_method)

            # The api my return a single record, or a result set
            # If a result set is returned, the key "results" will appear in the object
            # If  single object is returned the key will not appear
            # If multiple results are returned, we will try to find the right one
            # This is a workaround from the api having bugs

            # Create a var for the record returned
            record_body = None

            # If a single record is returned, store the result
            if "results" not in results.keys():
                record_body = results

            # If a result set was returned, we need to look for the the right record
            # Even if a single record is returned, it might not be the right one
            else:

                # If an empty result set is returned, stop here
                if len(results["results"]) == 0:
                    logger.debug("Empty result set returned by the api.")
                    return None

                # If more than one result was found, try to find the right onw
                else:

                    logger.debug("A result set with '{0}' records was returned..".format(len(results["results"]) ))
                    logger.debug("Using extra query logic to determine if the record was found.")

                    # Sometimes the API will lie and give us records which do not match the query string
                    # For exmpale, If I GET the following url
                    #   https://15.4.7.1/api/operatingsystems/29/os_default_templates?search=provisioning_template_id%3D161
                    # I will get back records who's provisioning_tepmlate_id do not equal 161
                    # We will have to implement our own query logic to weed out the bad results
                    # Basically we will check if the query key matches the value

                    matched_records = []

                    # Determine what record field and values are being used for the query
                    record_field, query_value = ForemanApiWrapper._determine_property_key_and_value_for_query_string(minimal_record)

                    # Check if any of the records in the result set contain the correct field and value
                    l = len(results["results"])
                    for x in range(0, l):
                        result_record_body = results["results"][x]

                        # Create a record to compare with the minimal record
                        result_record = {record_type: result_record_body}

                        # Check f the query key exists in both objects, and the values are the same
                        a = record_field in minimal_record[record_type].keys()
                        b = record_field in result_record[record_type].keys()
                        minimal_key_value = str(minimal_record[record_type][record_field])
                        tmp_key_value = str(result_record[record_type][record_field])
                        c = minimal_key_value == tmp_key_value

                        # As mentioned in the function to create the query string,
                        # sometimes the API will convert values to lower case for the GET
                        # It hasn't happened enough to require I tweak the mapping file yet
                        if record_field in ["mac"]:
                            c = minimal_key_value.lower() == tmp_key_value.lower()

                        # If a record satisfies the query, append it
                        if a and b and c:
                            logger.debug("Record at index '{0}' matched.".format(x))
                            matched_records.append(result_record)
                        else:
                            logger.debug("Record at index '{0}' did not match because:".format(x))
                            if not a:
                                logger.debug("  Query key '{0}' missing from minimal record.".format(record_field))
                            if not b:
                                logger.debug("  Query key '{0}' missing from actual record.".format(record_field))
                            if not c:
                                logger.debug("  Query key values did not match. '{0}' != '{1}'".format(minimal_key_value, tmp_key_value))

                    # If we were not able to identify a proper match, throw an exception
                    if len(matched_records) != 1:
                        err_str = "There were '{0}' records returned from the query when there should have only been one."
                        err_str += "Custom logic was not able to filter the results to a single record"
                        err_str = err_str.format(len(matched_records))
                        raise ForemanApiCallException(
                            err_str,
                            check_url,
                            http_method,
                            results,
                            None,
                            None)

                    record_body = matched_records[0][record_type]

            record = {record_type: record_body}

            return record
        except Exception as e:
            raise Exception("An error occurred while reading the record.") from e

    @staticmethod
    def _convert_record_for_api_method(http_method, record):

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
        if http_method not in ApiRecordPropertyNameMappings.keys():
            return record
        if record_type not in ApiRecordPropertyNameMappings[http_method].keys():
            return record

        required_changes = ApiRecordPropertyNameMappings[http_method][record_type]

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
            set_url = self._determine_api_endpoint_for_record(minimal_record, include_query=False)
            http_method = "POST"

            headers = ForemanApiWrapper._get_headers_for_http_method(http_method)

            # We may need to convert the record based on the API endpoint being used
            # The API is inconsistent in the way it represents data
            record_for_post = ForemanApiWrapper._convert_record_for_api_method(http_method, minimal_record)

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
            set_url = self._determine_api_endpoint_for_record(minimal_record)
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
            record_for_put = ForemanApiWrapper._convert_record_for_api_method(http_method, minimal_record)

            # The api call will expect the arguments in a certain form
            api_call_arguments = ForemanApiWrapper._get_api_call_arguments(record_for_put)
            record_type = ForemanApiRecord.get_record_type_from_record(minimal_record)
            updated_record_body = self.make_api_call(set_url, http_method, api_call_arguments, headers)
            updated_record = {record_type : updated_record_body}

            # Verify that the updated record has the same id as the minimal record
            # Raise an exception if it does not
            try:
                record_identifier_field, record_identifier = ForemanApiRecord.get_identifier_from_record(minimal_record)
                ForemanApiRecord.confirm_modified_record_identity(record_identifier, record_type, updated_record)
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
            base_delete_url = self._determine_api_endpoint_for_record(minimal_record, include_query=False)
            field, record_identifier = ForemanApiRecord.get_identifier_from_record(minimal_record)
            delete_url = "{0}/{1}".format(base_delete_url, record_identifier)

            http_method = "DELETE"

            # We may need to convert the record based on the API endpoint being used
            # The API is inconsistent in the way it represents data
            record_for_delete = ForemanApiWrapper._convert_record_for_api_method(http_method, minimal_record)

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
