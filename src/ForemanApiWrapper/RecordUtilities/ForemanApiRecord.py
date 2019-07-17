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


def get_identifier_from_record(record, mappings):

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

    # Set the defaults
    possibleKeys = ["name", "id"]

    # Override defaults with mapping file if applicable
    record_type = get_record_type_from_record(record)
    if record_type in mappings.keys():
        possibleKeys = mappings[record_type]

    record_body = get_record_body_from_record(record)
    for key in possibleKeys:
        if key in record_body.keys():
            return key, record_body[key]

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


def confirm_modified_record_identity(record_identifier, record_type, record_to_confirm):

    # The name or id fields on a record can be used to confirm identity
    # Using IDs is the safest choice, but not possible in all circomstances
    # For example, when deleting records, one may only know the name upfront

    try:
        record_to_confirm_type = get_record_type_from_record(record_to_confirm)

        if record_type != record_to_confirm_type:
            raise Exception("The record types did not match: '{0}' vs '{1}'.".format(record_type, record_to_confirm_type))

        identification_match = False

        try:
            id = get_id_from_record(record_to_confirm)
            if id == record_identifier:
                identification_match = True
        except:
            pass

        try:
            name = get_name_from_record(record_to_confirm)
            if name == record_identifier:
                identification_match = True
        except:
            pass

        if not identification_match:
            raise Exception("The record did' not match the identifier '{0}' supplied.".format(record_identifier))
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
