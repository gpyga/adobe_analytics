class ApiError(Exception):
    """ 
    Exception raised when user does not have appropriate credentials
    Used for 301 & 401 HTTP Status codes
    """
    def __init__(self, response):
        if 'error_description' in response:
            self.message = response['error_description'] 
        else:
            self.message = response['error']

