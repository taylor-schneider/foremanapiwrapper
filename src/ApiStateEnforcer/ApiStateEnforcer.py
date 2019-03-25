from ForemanApiUtilities.ForemanApiCallException import ForemanApiCallException
from RecordUtilities import RecordComparison
from ApiStateEnforcer.RecordModificationReceipt import RecordModificationReceipt

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

        reason = None
        change_required = False

        if desired_state.lower() == "present":
            if not actual_record:
                reason = self.missing_record_message
                change_required = True
            else:
                states_match = RecordComparison.compare_record_states(minimal_record, actual_record)
                change_required = not states_match

                if states_match:
                    reason = self.states_match_message
                else:
                    reason = self.record_mismatch_message

        if desired_state.lower() == "absent":
            if not actual_record:
                change_required = False
                reason = self.record_already_absent_message
            else:
                reason = self.extra_record_message
                change_required = True

        return change_required, reason

    def ensure_state(self, record_type, desired_state, minimal_record):

        # This function will ensure that a state for a given record
        # The supported states are "present" or "absent"
        # It wil use the Check() function to ask the foreman api if a record
        # with a matching id or name exists.
        # It will then create or delete the record as required
        # It will return an object which will report the information relevant
        # to any decisions oor actions taken
        #

        try:
            if desired_state.lower() not in ["present", "absent"]:
                raise Exception("The specified desired state '{0}' was not valid.".format(desired_state))

            # Get the current state
            # If the record doesn't exist, the api will throw a 404 which we can ignore
            original_record = None
            try:
                original_record = self.api_wrapper.read_record(record_type, minimal_record)
            except Exception as e:
                if type(e.__cause__) == ForemanApiCallException:
                    if e.__cause__.results.status_code != 404:
                        raise Exception("An unexpected error occurred while reading record.") from e

            # Determine what change is required (if any)
            change_required, reason = self._determine_change_required(desired_state, minimal_record, original_record)

            # If not change is required, our work is done
            if not change_required:
                return RecordModificationReceipt(
                    change_required,
                    reason,
                    minimal_record,
                    desired_state,
                    original_record,
                    None)

            # Do the change
            modified_record = None
            if reason == self.missing_record_message:
                modified_record = self.api_wrapper.create_record(record_type, minimal_record)
            elif reason == self.extra_record_message:
                modified_record = self.api_wrapper.delete_record(record_type, minimal_record)
            elif reason == self.record_mismatch_message:
                # Do the update rather than a delete / set
                # modifiedRecord = self.Delete(recordType, minimalRecordState)
                # modifiedRecord = self.Set(recordType, minimalRecordState)
                modified_record = self.api_wrapper.update_record(record_type, minimal_record)

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

