class ModifiedRecordMismatchException(Exception):

    def __init__(self, message, endpoint, httpMethod, httpMethodArgs, record):

        # Call the base class constructor with the parameters it needs
        super().__init__(message)

        # Now for your custom code...
        self.endpoint = endpoint
        self.httpMethod = httpMethod
        self.httpMethodArgs = httpMethodArgs
        self.record = record