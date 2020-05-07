class WemulateException(Exception):

    def __init__(self, code, message):
        Exception.__init__(self, code, message)
        self.message = f"Error {str(code)}: {message}"

    def __str__(self):
        return self.message
