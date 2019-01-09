class ForemanApiCallException(Exception):

    def __init__(self, message, endpoint, method, results, arguments=None, headers=None):

        # Call the base class constructor with the parameters it needs
        super().__init__(message)

        # Now for your custom code...
        self.endpoint = endpoint
        self.method = method
        self.results = results
        self.arguments=arguments
        self.headers=headers