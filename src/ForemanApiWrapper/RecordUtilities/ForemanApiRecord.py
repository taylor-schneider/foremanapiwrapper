from ForemanApiWrapper.ForemanApiUtilities.Mappings.ApiRecordIdentificationProperties import ApiRecordIdentificationProperties
from ForemanApiWrapper.RecordUtilities import RecordComparison
import logging


def get_record_type_from_record(record):
    try:
        keys = list(record.keys())
        if len(keys) > 2 or len(keys) <= 0:
            raise Exception("The record was malformed. It contained {0} keys.".format(len(keys)))

        # We can ignore the dependencies key
        keys = list(record.keys())
        if "dependencies" in keys:
            keys.remove("dependencies")
        record_type = keys[0]
        return record_type

    except Exception as e:
        raise Exception("Could not determine the record type from the record.") from e


def get_record_body_from_record(record):
    record_type = get_record_type_from_record(record)
    return record[record_type]


def get_record_identifcation_properties(record):
    # This function will return an ordered list of properties which can be used to identify a record
    # The order is intended to indicate the likelihood of producing a unique record
    # when used in a query

    record_type = get_record_type_from_record(record)

    # Start with the id and name fields
    identification_properties = ["id", "name"]

    # Some records have preferred identification properties
    # Retrieve them and add them to the list
    if record_type in ApiRecordIdentificationProperties.keys():
        identification_properties = ApiRecordIdentificationProperties[record_type]

    # Remove the keys that are not found on the record
    record_body = get_record_body_from_record(record)
    record_properties = list(record_body.keys())
    for identification_property in identification_properties.copy():
        if identification_property not in record_properties:
            identification_properties.remove(identification_property)

    # Dedupe the list
    identification_properties = list(set(identification_properties))

    # Raise an exception if the list is empty
    if len(identification_properties) == 0:
        raise Exception("Unable to determine identification properties for the record.")

    return identification_properties

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


def confirm_modified_record_identity(minimal_record, record_to_confirm):
    try:
        logging.debug("Confirming record identity")
        record_type = get_record_type_from_record(minimal_record)
        identification_field_names = get_record_identifcation_properties(minimal_record)
        for identification_field_name in identification_field_names:
            if identification_field_name in record_to_confirm[record_type].keys():
                logging.debug("Comparing field named {0}.".format(identification_field_name))
                minimal_value = minimal_record[record_type][identification_field_name]
                confirmation_value = minimal_record[record_type][identification_field_name]
                match, reason = RecordComparison._compare_primitives(record_type, minimal_value, confirmation_value, identification_field_name)
                if match:
                    logging.debug("Identity Confirmed")
                    return
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
