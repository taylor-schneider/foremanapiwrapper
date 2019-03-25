class RecordModificationReceipt:

    def __init__(self, changed, reason, minimal_record, desired_state, actual_record, original_record):
        self.changed = changed
        self.reason = reason
        self.minimal_record = minimal_record
        self.desired_state = desired_state
        self.actual_record = actual_record
        self.original_record = original_record