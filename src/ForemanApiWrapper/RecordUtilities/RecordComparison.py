from ForemanApiWrapper.RecordUtilities import ForemanApiRecord
from ForemanApiWrapper.ForemanApiUtilities.Mappings.ApiRecordPropertyNameMappings import ApiRecordPropertyNameMappings
from ForemanApiWrapper.RecordUtilities import ForemanApiRecord
import jsonpath
import os


def _normalize_primitive(minimal_primitive, actual_primitive):
    try:
        # Call the constructor of the minimal record type
        new_actual_record = type(minimal_primitive)(actual_primitive)
        actual_primitive = new_actual_record
        return actual_primitive, ""
    except:
        return actual_primitive, "The primitive could not be normalized."


def _compare_primitives(record_type, minimal_primitive, actual_primitive, primitive_key=None):

    reason = ""

    # Check that the two objects are the same type
    # If they are not, we want to allow for stupid humans
    # for example the human may specify a string but the API returns an int
    # See if we can convert the the actual into the type of the minimal
    if type(minimal_primitive) != type(actual_primitive):
        reason += " The objects will be normalized because the are not the same type. '{0}' vs. '{1}'.".format(type(minimal_primitive), type(actual_primitive))
        actual_primitive, tmp_reason = _normalize_primitive(minimal_primitive, actual_primitive)
        reason += tmp_reason

    # There are some exceptions to handle here
    #
    # 1. The host name field is different between the GET and POST/PUT
    # The name in the GET has the fqdn added to the end of the name
    # The POST/PUT is just the host name and it lacks the fqdn suffix
    # We will to our best to do the logic and make a comparison
    if primitive_key is not None:
        if record_type == "host" and primitive_key == "name":
            try:
                reason += " Adjusting the name field for the host."
                actual_primitive = actual_primitive.split(".")[0]
            except:
                pass

    match = minimal_primitive == actual_primitive

    if match:
        reason +=" The primitives matched."
    else:
        reason += " The primitives were compared as type '{0}' but values did not match: '{1}' vs '{2}'.".format(type(minimal_primitive), minimal_primitive, actual_primitive)

    reason = reason.strip(" ")

    return match, reason


def _compare_dicts(record_type, minimal_record_state, actual_record_state):

    actual_keys = list(actual_record_state.keys())

    dict_mismatch_message = "The dicts did not match."

    # Loop through the dict keys and compare the values
    for key, value in minimal_record_state.items():

        # If a key is missing from the actual record, that is a dead giveaway
        # There are some exceptions however... and they depend on the record type
        if key not in actual_keys:
            # Ignore exceptions
            #
            # 1. The subnet is created with an id for the doman. The resulting record has the domain name not the id
            #     There is no way to make this comparision
            if record_type == "subnet" and key == "domain_ids":
                continue
            # 2. The operatingsystem has an undocumented parameter config_template_ids on POST but not the others
            if record_type == "operatingsystem" and key == "config_template_ids":
                continue
            # 3. The provisioning_template allows you to specify an audit_comment when putting a record
            # This is like a commit message and does not show up on the get
            if record_type == "provisioning_template" and key == "audit_comment":
                continue
            # 4. The host has a root_pass field which is not returned on a GET
            # This parameter will have to be validated by the created_at field
            if record_type == "host" and key == "root_pass":
                continue

            # If not an exception call out the issue
            key_missing_message = "The key '{0}' was not found on the actual record.".format(key)
            return False, " ".join([dict_mismatch_message, key_missing_message])

        # Now that we have verified the key exist we can check the values for the key are equivalent
        minimal_value = minimal_record_state[key]
        actual_value = actual_record_state[key]

        # Now we compare the values
        comparison_result, reason = _compare_objects(record_type, minimal_value, actual_value, key)

        # Return if there was a mismatch
        if not comparison_result:
            key_mismatch_message = "The keys '{0}' did not match.".format(key)
            return False, " ".join([dict_mismatch_message, key_mismatch_message, reason])

    # If we got here without exiting, we match!
    return True, "All the keys and values in the dict match."


def _compare_lists(record_type, minimal_record_state, actual_record_state):

    list_mismatch_message = "The lists did not match."

    # If the minimal state list is larger than the actual state,
    # something is definitely missing
    if len(minimal_record_state) > len(actual_record_state):
        length_mismatch_message = "The minimal record list length was '{0}' compared to '{1}'.".format(len(minimal_record_state), len(actual_record_state))
        return False, " ".join([list_mismatch_message, length_mismatch_message])

    # Lists are a bit complicated to compare
    # We are not enforcing order here
    # We will need to compare a given element of the minimal state
    # with all the elements of the actual state to find a match
    # If there is one match we will continue on
    # If there are no matches we have an issue
    for x in range(0, len(minimal_record_state)):
        match = False
        reason = None
        a = minimal_record_state[x]
        for b in actual_record_state:
            match, reason = _compare_objects(record_type, a, b)
            if match:
                break
        if not match:
            element_mismatch_message = "There was no match for element in list at index '{0}'.".format(x)
            return False, " ".join([list_mismatch_message, element_mismatch_message])

    # If we got here without exiting, we match!
    return True, "All the elements in the list match."


def _compare_objects(record_type, minimal_record, actual_record, record_key=None):
    # This function will return true or false based on whether or not the
    # actual state represents the minimal state
    #       Ie. All the keys/values in minimal state exist in actual
    # There is a lot of hackery to make this work

    match = False
    reason = ""

    object_mismatch_message = "The objects did not match."

    # Certain non primitives need to be handled separately
    # Dictionaries are an example of this
    if isinstance(minimal_record, dict):
        # The Foreman API is not consistent with the property names used by records
        # The property names change depending on the http method used for the api endpoint
        # For example the subnet record will use the domain_ids or domains property
        # depending on which http method we use.
        # We will need to do some logic to "normalize the property names"
        # loop through the properties in the minimal state
        # If the property is not found, check to see if it has an alternate name
        # If both the property and the alternate name are not found, return false

        match, reason = _compare_dicts(record_type, minimal_record, actual_record)

    # Lists are also an example of this issue
    elif isinstance(minimal_record, list):
        match, reason = _compare_lists(record_type, minimal_record, actual_record)

    # primitive objects should compare just fine
    else:
        match, reason = _compare_primitives(record_type, minimal_record, actual_record, record_key)

    if match:
        reason +="The obects matched."
    else:
        reason = " ".join([object_mismatch_message, reason])

    reason = reason.strip()

    return match, reason


def normalize_record_properties_for_http_method(actual_record):
    # The Foreman API is not consistent with the property names used by records
    # The property names change depending on the http method used for the api endpoint
    # For example the subnet record will use the domain_ids or domains property
    # depending on which http method we are using and whether we are providing a payload
    # or receiving results.
    # I have defined the system such that the actual record will be transformed to conform
    # the minimal record through the mappings in the mapping file

    try:
        # Get some data used for resolving the mapping
        record_type = ForemanApiRecord.get_record_type_from_record(actual_record)
        record_body = ForemanApiRecord.get_record_body_from_record(actual_record)

        # Loop through the record's properties and perform transformations if necessary
        normalized_record_body = record_body
        for actual_record_property_name, actual_record_property_value in record_body.items():

            # Ignore record types that do not have mappings defined
            if record_type not in ApiRecordPropertyNameMappings.keys():
                continue

            # Get the property mapping object
            try:
                property_mappings = [x for x in ApiRecordPropertyNameMappings[record_type] if x["actual_record_property"] == actual_record_property_name]
                if len(property_mappings) > 1:
                    raise Exception("Too many mappings were defined for the actual record'{0}' property of the '{1}' record type.".format(actual_record_property_name, record_type))
                elif len(property_mappings) == 0:
                    continue
                else:
                    property_mapping = property_mappings[0]
            except Exception as ex:
                raise Exception("An error occurred while examining ApiRecordPropertyNameMappings.") from ex


            # Resolve the jsonpath expression
            jsonpath_string = property_mapping["jsonpath"]
            new_property_value = jsonpath.jsonpath(actual_record, jsonpath_string)

            # If the path we are searching for does not exist, false is returned
            # this can happen if for example, the domains list is empty and we
            # are tyring to access an id property from an element in the list
            # In this case, we will just deal with an empty list
            if new_property_value == False:
                new_property_value = []

            # The json path library will always return a list if the path exists
            # In some cases, we want the query to return a single result rather than a list
            # We have a field to denote whether the user wants to pull out a single value or not
            # If no results exist,
            if not property_mapping["multiple_results"]:
                if len(new_property_value) == 0:
                    raise Exception("The mapping did not resolve to a single value for the actual record'{0}' property of the '{1}' record type.".format(actual_record_property_name, record_type))
                else:
                    new_property_value = new_property_value[0]

            # Set the property value
            new_property_name = property_mapping["minimal_record_property"]
            normalized_record_body[new_property_name] = new_property_value
            # Remove the old property
            normalized_record_body.pop(actual_record_property_name)

        normalized_record = { record_type : normalized_record_body}
        return normalized_record
    except Exception as e:
        raise Exception("An error occurred while normalizing the record.") from e


def compare_records(minimal_record, actual_record):

    # First we need to remove any dependencies from the record
    # The dependencies property is something that is not part of the api
    # We added it to make this code work
    clean_minimal_record = ForemanApiRecord.remove_dependencies_from_record(minimal_record)
    actual_record = ForemanApiRecord.remove_dependencies_from_record(actual_record)
    record_type = ForemanApiRecord.get_record_type_from_record(minimal_record)

    # Next we will transform the actual record so that it matches the minimal record's schema
    normalized_actual_record = normalize_record_properties_for_http_method(actual_record)

    # Now do the comparison
    # We will determine whether or not two objects match as well as a human friendly reason they mismatch
    match, reason = _compare_objects(record_type, clean_minimal_record, normalized_actual_record)

    # Return the results
    return match, reason
