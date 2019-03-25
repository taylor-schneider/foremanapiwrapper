def get_name_or_id_from_record(record):
    # The state will show what an object should look like
    # For example:
    #    {
    #        "name": "some_environment"
    #    }

    possibleKeys = ["name", "id"]
    for key in possibleKeys:
        if key in record.keys():
            return key, record[key]

    raise Exception("Could not determine the name or id from record.")


def get_record_type_from_record(record):
    try:
        keys = list(record.keys())
        if len(keys) != 1:
            raise Exception("The record was malformed. It contained {0} keys.".format(len(keys)))

        recordType = keys[0]
        return recordType

    except Exception as e:
        raise Exception("Could not determine the record type from the record.") from e


def confirm_modified_record_identity(name_or_id, record):

    # this function will return true or false based on whether or not
    # The name_or_id specified matches the record supplied

    if "name" in record.keys():
        if record["name"] == name_or_id:
            return True
    if "id" in record.keys():
        if record["id"] == name_or_id:
            return True
    return False

