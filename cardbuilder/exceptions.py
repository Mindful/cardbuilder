class CardBuilderUsageException(Exception):
    """An exception class representing cases where something has been used incorrectly. These typically shouldn't be
    caught outside tests, as they likely can't be resolved without config and/or code changes."""
    def __init__(self, text):
        super().__init__(text)


class CardBuilderException(Exception):
    def __init__(self, text):
        super().__init__(text)


class WordLookupException(CardBuilderException):
    def __init__(self, text):
        super().__init__(text)


class FieldLookupException(CardBuilderException):
    def __init__(self, text):
        super().__init__(text)


class CardResolutionException(CardBuilderException):
    def __init__(self, text):
        super().__init__(text)
