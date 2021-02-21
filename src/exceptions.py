class CardBuilderException(Exception):
    def __init__(self, text):
        super().__init__(text)


class WordLookupException(CardBuilderException):
    def __init__(self, text):
        super().__init__(text)


class CardResolutionException(CardBuilderException):
    def __init__(self, text):
        super().__init__(text)