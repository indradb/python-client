class Error(Exception):
    def __init__(self, error, code=None):
        super(Error, self).__init__()
        self.code = code
        self.error = error

    def __str__(self):
        if self.code:
            return "[%s] %s" % (self.code, self.error)
        else:
            return self.error
