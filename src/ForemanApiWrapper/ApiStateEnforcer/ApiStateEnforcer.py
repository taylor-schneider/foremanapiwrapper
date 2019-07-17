import logging
import json
import os
from ForemanApiWrapper.ForemanApiUtilities.ForemanApiCallException import ForemanApiCallException
from ForemanApiWrapper.RecordUtilities import RecordComparison
from ForemanApiWrapper.ApiStateEnforcer.RecordModificationReceipt import RecordModificationReceipt
from ForemanApiWrapper.RecordUtilities import ForemanApiRecord


logger = logging.getLogger()


class ApiStateEnforcer():

    record_mismatch_message = "The actual record did not match the desired record."
    record_already_absent_message = "The record is already absent."
    missing_record_message = "The record does not exist and it should."
    extra_record_message = "The record exists and it should not."
    states_match_message = "The actual state matches the desired state."

    def __init__(self, api_wrapper):
        self.api_wrapper = api_wrapper

    def _determine_change_required(self, desired_state, minimal_record, actual_record):

        # This function will determine whether the minimal record is represented by the actual record.
        # If any of the properties of the minimal record do not match or are missing,
        # this function will return True denoting that a change is required.
        # It will also give a reason for why the decision was made.
        #

        reason = None
        change_required = False

        if desired_state.lower() == "present":
            if not actual_record:
                reason = self.missing_record_message
                change_required = True
            else:
                states_match, reason_message = RecordComparison.compare_records(minimal_record, actual_record)
                change_required = not states_match

                if states_match:
                    reason = self.states_match_message + reason_message
                else:
                    reason = self.record_mismatch_message + reason_message

        if desired_state.lower() == "absent":
            if not actual_record:
                change_required = False
                reason = self.record_already_absent_message
            else:
                reason = self.extra_record_message
                change_required = True

        return change_required, reason

    def ensure_state(self, desired_state, minimal_record):

        # This function will ensure that a state for a given record
        # The supported states are "present" or "absent"
        # It wil use the Check() function to ask the foreman api if a record
        # with a matching id or name exists.
        # It will then create or delete the record as required
        # It will return an object which will report the information relevant
        # to any decisions oor actions taken
        #

        try:
            logger.debug("Ensuring record is '{0}'".format(desired_state))

            if desired_state.lower() not in ["present", "absent"]:
                raise Exception("The specified desired state '{0}' was not valid.".format(desired_state))

            record_type = ForemanApiRecord.get_record_type_from_record(minimal_record)

            # Get the current state as some fields may exist which are not present on our minimal state represenation
            # If the record doesn't exist, the api will throw a 404 which we can ignore
            logger.debug("Getting the current state.")

            original_record = None
            try:
                original_record = self.api_wrapper.read_record(minimal_record)
            except Exception as e:
                ignore_exception = False
                if type(e.__cause__) == ForemanApiCallException:
                    if e.__cause__.results is not None:
                        if "status_code" in dir(e.__cause__.results):
                            if e.__cause__.results.status_code == 404:
                                logger.debug("Ignoring 404 Exception as it indicates the record does not exist.")
                                ignore_exception = True
                        else:
                            logger.debug("Ignoring exception raised by API failing to perform query properly.")
                            ignore_exception = True
                if not ignore_exception:
                    raise Exception("An unexpected error occurred while reading record.") from e

            # Determine what change is required (if any)
            # The actual state needs to be compared with a minimal state to determine if
            # any fields are missing or need to be changed
            # The property names change depending on the http method used for
            # the api endpoint
            # We will need to do some logic to "normalize the property names"
            # loop through the properties in the minimal state
            # If the property is not found, check to see if it has an alternate name
            # If both the property and the alternate name are not found, return false

            change_required, reason = self._determine_change_required(desired_state, minimal_record, original_record)

            # Print some debug info about the change required
            logger.debug("Change required: '{0}'".format(change_required))
            logger.debug("Reason: '{0}'".format(reason))
            logger.debug("Actual Record:")
            obj_json = json.dumps(original_record, indent=4, sort_keys=True)
            for line in obj_json.split(os.linesep):
                logger.debug(line)
            logger.debug("Desired Record:")
            obj_json = json.dumps(minimal_record, indent=4, sort_keys=True)
            for line in obj_json.split(os.linesep):
                logger.debug(line)

            # If not change is required, our work is done
            if not change_required:
                return RecordModificationReceipt(
                    change_required,
                    reason,
                    minimal_record,
                    desired_state,
                    original_record,
                    original_record) # The actual and original records will be the same

            # Do the change
            modified_record = None
            if reason.startswith(self.missing_record_message):
                logger.debug("Creating the missing record.")
                modified_record = self.api_wrapper.create_record(minimal_record)
            elif reason.startswith(self.extra_record_message):
                logger.debug("Deleting the record.")
                # If a change is required, the original record will contain an id
                # We will need to add this to the minimal_record if it had not already been added
                id = ForemanApiRecord.get_id_from_record(original_record)
                minimal_record[record_type]["id"] = id
                modified_record = self.api_wrapper.delete_record(minimal_record)
            elif reason.startswith(self.record_mismatch_message):
                # Do the update rather than a delete / set
                # If a change is required, the original record will contain an id
                # We will need to add this to the minimal_record if it had not already been added
                id = ForemanApiRecord.get_id_from_record(original_record)
                minimal_record[record_type]["id"] = id
                logger.debug("Updating the record.")
                modified_record = self.api_wrapper.update_record(minimal_record)

            # Return the results
            return RecordModificationReceipt(
                change_required,
                reason,
                minimal_record,
                desired_state,
                modified_record,
                original_record)

        except Exception as e:
            raise Exception("An error occurred while ensuring the api state.") from e

