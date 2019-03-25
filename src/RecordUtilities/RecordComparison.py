def _compare_dicts(minimal_record_state, actual_record_state):

    actual_keys = list(actual_record_state.keys())

    # If a key is missing that is a dead givaway
    for key, value in minimal_record_state.items():
        if key not in actual_keys:
            return False

        # Call this function recursively
        # Return false if any of the keys dont match

        minimal_value = minimal_record_state[key]
        actual_value = actual_record_state[key]

        comparison_result = compare_record_states(minimal_value, actual_value)
        if not comparison_result:
            return False

    # If we got here without exiting, we match!
    return True


def _compare_lists(minimal_record_state, actual_record_state):

    # If the minimal state list is smaller than the actual state,
    # something is definitely missing
    if len(minimal_record_state) > len(actual_record_state):
        return False

    # Lists are a bit complicated to compare
    # We are not enforcing order here
    # We will need to compare a given element of the minimal state
    # with all the elements of the actual state to find a match
    for x in range(0, len(minimal_record_state)):
        match = False
        a = minimal_record_state[x]
        for b in actual_record_state:
            match = compare_record_states(a, b)
            if match:
                break
        if not match:
            return False

    # If we got here without exiting, we match!
    return True


def compare_record_states(minimal_record_state, actual_record_state):
    # This function will return true or false based on whether or not the
    # actual state represents the minimal state
    #       Ie. All the keys/values in minimal state exist in actual

    # Check that the two objects are the same type
    if type(minimal_record_state) != type(actual_record_state):
        return False

    # Now that we know the objects are the same, we can compare

    # Certain non primitives need to be handled separately

    # Dictionaries are an example of this
    if isinstance(minimal_record_state, dict):
        match = _compare_dicts(minimal_record_state, actual_record_state)
        return match

    # Lists are also an example of this issue
    if isinstance(minimal_record_state, list):
        match = _compare_lists(minimal_record_state, actual_record_state)
        return match

    # lists and other objects should compare just fine
    else:
        return minimal_record_state == actual_record_state
