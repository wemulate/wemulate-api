class WemulateException(Exception):

    def __init__(self, code, message):
        self.message = f"Statuscode: {str(code)} : {message}"

    def __str__(self):
        return self.message
