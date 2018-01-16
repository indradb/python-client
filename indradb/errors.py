class Error(Exception):
    def __init__(self, code, error):
        super(Error, self).__init__()
        self.code = code
        self.error = error

    def __str__(self):
        return "[%s] %s" % (self.code, self.error)
