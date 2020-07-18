class ImageHttpError(Exception):
    def __init__(self, message, res = None):
        self.res = res
        self.message = message
        super().__init__(message)

    def __str__(self):
        if self.res:
            return f"status code: {res.status_code} -> {self.message}"
        return self.message