class ApiStateEnforcerException(Exception):

    def __init__(self, message, minimalState, actualState):

        # Call the base class constructor with the parameters it needs
        super().__init__(message)

        # Now for your custom code...
        self.minimalState = minimalState
        self.actualState = actualState