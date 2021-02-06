class LookupExceptinon(RuntimeError):
    def __init__(self, text):
        super().__init__(text)