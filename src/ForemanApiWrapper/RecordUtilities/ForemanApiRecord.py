from ForemanApiWrapper.ForemanApiUtilities.Mappings.ApiRecordIdentificationProperties import ApiRecordIdentificationProperties

def get_record_type_from_record(record):
    try:
        keys = list(record.keys())
        if len(keys) > 2 or len(keys) <= 0:
            raise Exception("The record was malformed. It contained {0} keys.".format(len(keys)))

        # We can ignore the dependencies key
        keys = list(record.keys())
        if "dependencies" in keys:
            keys.remove("dependencies")
        recordType = keys[0]
        return recordType

    except Exception as e:
        raise Exception("Could not determine the record type from the record.") from e


def get_record_body_from_record(record):
    record_type = get_record_type_from_record(record)
    return record[record_type]


def get_record_identifcation_properties(record):
    # This function will return an ordered list of properties which can be used to identify a record
    # The order is intended to indicate the likelihood of producing a unique record
    # when used in a query
    record_body = get_record_body_from_record(record)
    record_properties = list(record_body.keys())
    record_type = get_record_type_from_record(record)
    preferred_keys = []

    # Some records have preferred identification properties
    if record_type in ApiRecordIdentificationProperties.keys():
        preferred_keys = ApiRecordIdentificationProperties[record_type]

    # If the id was not listed, make sure it is at the front of the list
    if "id" not in record_body.keys() and "id" not in record_body.keys():
        preferred_keys = ["id"] + preferred_keys

    # Remove the keys that are not found on the record
    for preferred_key in preferred_keys.copy():
        if preferred_key not in record_properties:
            preferred_keys.remove(preferred_key)

    record_properties = preferred_keys + record_properties
    record_properties = list(set(record_properties))
    return record_properties


def get_identifier_from_record(record):

    # When checking if a record exists, several fields can be used
    # The name nad id fields are generally interchangable
    # an example record:
    #   {
    #       environment:  {
    #           "name": "some_environment"
    #       }
    #   }
    # In some cases the API is not consistent and other fields are used
    # The exceptions to the rule are stored in the mappings
    #
    # This function will return a tuple containing the field name and the value
    #

    identifier_fields = get_record_identifcation_properties(record)
    record_body = get_record_body_from_record(record)
    for identifier_field in identifier_fields:
        if identifier_field in record_body.keys():
            identifier_field_value = record_body[identifier_field]
            return identifier_field, identifier_field_value

    raise Exception("Could not determine the identifier for the record.")


def get_id_from_record(record):
    record_body = get_record_body_from_record(record)
    if "id" in record_body.keys():
        return record_body["id"]
    else:
        raise Exception("Unable to determine id for record.")


def get_name_from_record(record):
    record_body = get_record_body_from_record(record)
    if "name" in record_body.keys():
        return record_body["name"]
    else:
        raise Exception("Unable to determine name for record.")


def get_name_or_id_from_record(record):

    record_body = get_record_body_from_record(record)
    if "id" in record_body.keys():
        return "id", record_body["id"]
    elif "name" in record_body.keys():
        return "name", record_body["name"]
    else:
        raise Exception("Unable to determine name or id for record.")


def confirm_modified_record_identity(record_identifier, record_type, record_to_confirm):

    # The name or id fields on a record can be used to confirm identity
    # Using IDs is the safest choice, but not possible in all circumstances
    #       For example, when deleting records, one may only know the name upfront
    # In some cases other fields may be used based on the record type
    #       They are specified in the mappings
    # The record_identifier is a value for on of identifier fields
    # We need to check that the record_to_confirm has an identifier field with this value

    try:
        record_to_confirm_type = get_record_type_from_record(record_to_confirm)

        if record_type != record_to_confirm_type:
            raise Exception("The record types did not match: '{0}' vs '{1}'.".format(record_type, record_to_confirm_type))

        identifier_fields = get_record_identifcation_properties(record_to_confirm)
        record_body = get_record_body_from_record(record_to_confirm)

        for identifier_field in identifier_fields:
            if record_body[identifier_field] == record_identifier:
                return

        raise Exception("The record did not match the identifier '{0}' supplied.".format(record_identifier))
    except Exception as e:
        raise Exception("The record identity could not be confirmed.") from e


def remove_dependencies_from_record(record):
    new_record = record.copy()
    if "dependencies" in new_record.keys():
        new_record.pop("dependencies")
    return new_record


def get_record_dependencies(record):
    if "dependencies" in record.keys():
        return record["dependencies"]
    else:
        return None
